from __future__ import annotations

import argparse
import json
import platform
import sys
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from peerfix_core.dcr import compute_dcr, summarize_dcr
from peerfix_core.fidelity import evaluate_fidelity_bundle
from peerfix_core.generators import GeneratorSpec, build_generator
from peerfix_core.hashing import hash_dataframe, canonical_json_hash
from peerfix_core.icd import evaluate_icd_matched_n, evaluate_icd_legacy_full_n
from peerfix_core.protocol import validate_gate04_preflight
from peerfix_core.seeds import derive_seed
from peerfix_core.sensitivity import (
    calibrate_response_jitter,
    sensitivity_noise_seed,
    wrap_generator_with_response_jitter,
)
from peerfix_core.splits import repeated_group_condition_kfold, repeated_row_kfold
from peerfix_core.utility import evaluate_generator_utility


GENERATORS = ("gaussian_copula", "ctgan", "tvae", "tabddpm")
SCENARIOS = ("baseline_0pct", "sensitivity_1pct")
GEOMETRIES = ("row", "grouped_condition")
MASTER_SEED = 123
N_SYNTHETIC = 140
PRIMARY_N_REPEATS = 10
N_SPLITS = 5
ICD_SUBSAMPLES = 1000
MODEL_PANEL = ("lr", "rf", "gbr", "mlp")
LAMBDA_SENSITIVITY = (0.00, 0.05, 0.10, 0.20)


def _jsonable(v: Any) -> Any:
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        return float(v)
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, Path):
        return str(v)
    return v


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, default=_jsonable) + "\n",
        encoding="utf-8",
    )


def _factor_support(real: pd.DataFrame, factors: list[str]) -> dict[str, list[float]]:
    return {
        c: sorted(pd.to_numeric(real[c], errors="raise").astype(float).unique().tolist())
        for c in factors
    }


def _group_series(real: pd.DataFrame, factors: list[str]) -> pd.Series:
    return real[factors].astype(str).agg("|".join, axis=1)


def _generator_for(
    name: str,
    scenario: str,
    support: dict[str, list[float]],
    target: str,
    *,
    smoke: bool,
):
    spec = GeneratorSpec(name=name, factor_support=support)
    base = build_generator(spec, smoke=smoke)
    if scenario == "baseline_0pct":
        return base
    if scenario == "sensitivity_1pct":
        return wrap_generator_with_response_jitter(
            base,
            target=target,
            percent=1.0,
            scenario=scenario,
        )
    raise KeyError(scenario)


def _environment_summary() -> dict[str, Any]:
    out: dict[str, Any] = {
        "python": sys.version,
        "platform": platform.platform(),
    }
    for module_name in ["numpy", "pandas", "scipy", "sklearn", "statsmodels", "sdv", "torch"]:
        try:
            mod = __import__(module_name)
            out[module_name] = getattr(mod, "__version__", "unknown")
        except Exception as exc:
            out[module_name] = f"unavailable:{exc}"
    return out


def _prediction_manifest(preds: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    keys = ["scenario", "generator", "repeat", "fold", "model", "regime"]
    for key, g in preds.groupby(keys, sort=True):
        g2 = g.sort_values("row_id")[["row_id", "y_true", "y_pred", "model_seed"]].reset_index(drop=True)
        row = dict(zip(keys, key))
        row["downstream_seed"] = int(g2["model_seed"].iloc[0])
        row["predictions_hash"] = hash_dataframe(g2)
        row["n_predictions"] = int(len(g2))
        rows.append(row)
    return pd.DataFrame(rows)


def _augment_fold_manifest(
    manifest: pd.DataFrame,
    *,
    real: pd.DataFrame,
    preflight: dict[str, Any],
    geometry: str,
    scenario: str,
    factors: list[str],
    target: str,
) -> pd.DataFrame:
    groups = _group_series(real, factors)
    out = manifest.copy()
    out.insert(0, "dataset_sha256", preflight["dataset_sha256"])
    out.insert(1, "protocol_sha256", preflight["protocol_sha256"])
    out.insert(2, "geometry", geometry)
    split_seeds: list[int] = []
    train_groups: list[str] = []
    test_groups: list[str] = []
    noise_seeds: list[Any] = []
    sigmas: list[Any] = []
    cal_min: list[Any] = []
    cal_max: list[Any] = []

    for _, row in out.iterrows():
        repeat = int(row["repeat"])
        split_seeds.append(
            MASTER_SEED
            if geometry == "row"
            else derive_seed(MASTER_SEED, purpose="group_split", repeat=repeat)
        )
        tr_ids = list(row["train_row_ids"])
        te_ids = list(row["test_row_ids"])
        train_groups.append(json.dumps(sorted(set(groups.iloc[tr_ids].tolist()))))
        test_groups.append(json.dumps(sorted(set(groups.iloc[te_ids].tolist()))))

        if scenario == "sensitivity_1pct":
            gseed = int(row["generator_seed"])
            cal = calibrate_response_jitter(real.iloc[tr_ids], target=target, percent=1.0)
            noise_seeds.append(sensitivity_noise_seed(gseed, scenario=scenario))
            sigmas.append(cal.sigma)
            cal_min.append(cal.real_min)
            cal_max.append(cal.real_max)
        else:
            noise_seeds.append(None)
            sigmas.append(None)
            cal_min.append(None)
            cal_max.append(None)

    out["split_seed"] = split_seeds
    out["train_group_ids"] = train_groups
    out["test_group_ids"] = test_groups
    out["sensitivity_noise_seed"] = noise_seeds
    out["sensitivity_sigma"] = sigmas
    out["sensitivity_calibration_min"] = cal_min
    out["sensitivity_calibration_max"] = cal_max
    out["train_row_ids"] = out["train_row_ids"].map(json.dumps)
    out["test_row_ids"] = out["test_row_ids"].map(json.dumps)
    out["warnings"] = out["warnings"].map(json.dumps)
    out["exceptions"] = out["exceptions"].map(json.dumps)
    return out


def _selected_splits(real: pd.DataFrame, factors: list[str], geometry: str, repeat_start: int, repeat_end: int):
    if geometry == "row":
        all_splits = repeated_row_kfold(
            len(real), n_splits=N_SPLITS, n_repeats=PRIMARY_N_REPEATS, seed=MASTER_SEED
        )
    else:
        all_splits = repeated_group_condition_kfold(
            _group_series(real, factors),
            n_splits=N_SPLITS,
            n_repeats=PRIMARY_N_REPEATS,
            master_seed=MASTER_SEED,
        )
    return [s for s in all_splits if repeat_start <= s.repeat <= repeat_end]


def run_utility(args: argparse.Namespace, preflight: dict[str, Any], real: pd.DataFrame) -> None:
    factors = list(preflight["factors"])
    target = str(preflight["target"])
    support = _factor_support(real, factors)
    smoke = bool(args.smoke)
    repeat_start, repeat_end = (1, 1) if smoke else (args.repeat_start, args.repeat_end)
    n_selected_repeats = repeat_end - repeat_start + 1
    n_synthetic = 40 if smoke else N_SYNTHETIC
    models = ("lr",) if smoke else MODEL_PANEL
    splits = _selected_splits(real, factors, args.geometry, repeat_start, repeat_end)

    generator_fn = _generator_for(args.generator, args.scenario, support, target, smoke=smoke)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    run_id = canonical_json_hash(
        {
            "protocol_sha256": preflight["protocol_sha256"],
            "dataset_sha256": preflight["dataset_sha256"],
            "phase": "utility",
            "generator": args.generator,
            "scenario": args.scenario,
            "geometry": args.geometry,
            "repeat_start": repeat_start,
            "repeat_end": repeat_end,
            "smoke": smoke,
        }
    )[:16]

    try:
        metrics, manifest, preds = evaluate_generator_utility(
            real,
            target=target,
            splits=splits,
            generator_name=args.generator,
            generator_fn=generator_fn,
            n_synthetic=n_synthetic,
            master_seed=MASTER_SEED,
            scenario=args.scenario,
            model_names=models,
            return_predictions=True,
        )
        manifest = _augment_fold_manifest(
            manifest,
            real=real,
            preflight=preflight,
            geometry=args.geometry,
            scenario=args.scenario,
            factors=factors,
            target=target,
        )
        pred_manifest = _prediction_manifest(preds)
        metrics.insert(0, "geometry", args.geometry)
        metrics.insert(0, "protocol_sha256", preflight["protocol_sha256"])
        metrics.insert(0, "dataset_sha256", preflight["dataset_sha256"])

        metrics.to_csv(outdir / "repeat_level_metrics.csv", index=False)
        manifest.to_csv(outdir / "fold_manifest.csv", index=False)
        preds.to_csv(outdir / "heldout_predictions.csv", index=False)
        pred_manifest.to_csv(outdir / "prediction_manifest.csv", index=False)

        expected_folds = N_SPLITS * n_selected_repeats
        expected_repeat_model_rows = n_selected_repeats * len(models)
        if len(manifest) != expected_folds:
            raise RuntimeError(f"incomplete fold set: {len(manifest)} != {expected_folds}")
        if len(metrics) != expected_repeat_model_rows:
            raise RuntimeError(
                f"incomplete repeat/model metrics: {len(metrics)} != {expected_repeat_model_rows}"
            )
        expected_pred_groups = expected_folds * len(models) * 3
        if len(pred_manifest) != expected_pred_groups:
            raise RuntimeError(
                f"incomplete prediction manifest: {len(pred_manifest)} != {expected_pred_groups}"
            )

        _write_json(
            outdir / "completion.json",
            {
                "status": "PASS",
                "scientific": not smoke,
                "run_id": run_id,
                "phase": "utility",
                "generator": args.generator,
                "scenario": args.scenario,
                "geometry": args.geometry,
                "repeat_start": repeat_start,
                "repeat_end": repeat_end,
                "expected_folds": expected_folds,
                "observed_folds": int(len(manifest)),
                "expected_repeat_model_rows": expected_repeat_model_rows,
                "observed_repeat_model_rows": int(len(metrics)),
                "elapsed_seconds": time.time() - started,
                "preflight": preflight,
                "environment": _environment_summary(),
            },
        )
    except Exception as exc:
        _write_json(
            outdir / "failure.json",
            {
                "status": "FAIL",
                "scientific": not smoke,
                "run_id": run_id,
                "phase": "utility",
                "generator": args.generator,
                "scenario": args.scenario,
                "geometry": args.geometry,
                "repeat_start": repeat_start,
                "repeat_end": repeat_end,
                "elapsed_seconds": time.time() - started,
                "exception": repr(exc),
                "preflight": preflight,
                "environment": _environment_summary(),
            },
        )
        raise


def _flatten_fidelity(bundle: dict[str, object]) -> dict[str, Any]:
    continuous = bundle["continuous"]
    support = bundle["support"]
    corr = bundle["correlation"]
    doe = bundle["doe"]
    assert isinstance(continuous, pd.DataFrame)
    assert isinstance(support, pd.DataFrame)
    assert isinstance(corr, dict)
    assert isinstance(doe, dict)
    yrow = continuous.iloc[0]
    return {
        "ks_statistic": float(yrow["ks_statistic"]),
        "wasserstein_distance": float(yrow["wasserstein_distance"]),
        "mean_factor_support_coverage": float(support["support_coverage"].mean()),
        "mean_factor_tvd": float(support["total_variation_distance"].mean()),
        "max_off_support_fraction": float(support["off_support_fraction"].max()),
        **{k: float(v) for k, v in corr.items()},
        **{k: float(v) for k, v in doe.items()},
    }


def _icd_lambda_columns(prefix: str, result: dict[str, object]) -> dict[str, float]:
    base = float(np.mean([result["mean_S"], result["mean_M"], result["mean_D"]]))
    r = float(result["spurious_rate"])
    out: dict[str, float] = {}
    for lam in LAMBDA_SENSITIVITY:
        label = f"{lam:.2f}".replace(".", "p")
        out[f"{prefix}_lambda_{label}"] = float(base - lam * r)
    return out


def run_full_realisations(args: argparse.Namespace, preflight: dict[str, Any], real: pd.DataFrame) -> None:
    factors = list(preflight["factors"])
    target = str(preflight["target"])
    support = _factor_support(real, factors)
    smoke = bool(args.smoke)
    generator_fn = _generator_for(args.generator, args.scenario, support, target, smoke=smoke)
    outdir = Path(args.output_dir)
    synth_dir = outdir / "synthetic_realisations"
    synth_dir.mkdir(parents=True, exist_ok=True)
    n_synthetic = 40 if smoke else N_SYNTHETIC
    n_subsamples = 20 if smoke else ICD_SUBSAMPLES
    realisations = [1] if smoke else list(range(args.realisation_start, args.realisation_end + 1))

    rows: list[dict[str, Any]] = []
    effect_rows: list[pd.DataFrame] = []
    legacy_effect_rows: list[pd.DataFrame] = []
    dcr_rows: list[dict[str, Any]] = []
    fidelity_cont_rows: list[pd.DataFrame] = []
    fidelity_support_rows: list[pd.DataFrame] = []
    fidelity_multi_rows: list[dict[str, Any]] = []
    started_all = time.time()

    for realisation in realisations:
        started = time.perf_counter()
        generator_seed = derive_seed(
            MASTER_SEED,
            purpose="generator_full",
            scenario=args.scenario,
            generator=args.generator,
            realisation=realisation,
        )
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                synth = generator_fn(real, n_synthetic, generator_seed)
                synth_hash = hash_dataframe(synth)
                synth_path = synth_dir / f"realisation_{realisation:02d}.csv"
                synth.to_csv(synth_path, index=False)

                icd_primary = evaluate_icd_matched_n(
                    real, synth, target=target, factors=factors,
                    reference_terms=["kh2po4_pv"], matched_n=len(real),
                    n_subsamples=n_subsamples, lam=0.10, master_seed=MASTER_SEED,
                    scenario=args.scenario, generator=args.generator, realisation=realisation,
                )
                icd_secondary = evaluate_icd_matched_n(
                    real, synth, target=target, factors=factors,
                    reference_terms=["kh2po4_pv", "urea_pv:ammonium_sulfate_pv"],
                    matched_n=len(real), n_subsamples=n_subsamples, lam=0.10,
                    master_seed=MASTER_SEED, scenario=args.scenario,
                    generator=args.generator, realisation=realisation,
                )
                legacy_primary = evaluate_icd_legacy_full_n(
                    real, synth, target=target, factors=factors,
                    reference_terms=["kh2po4_pv"], lam=0.10,
                )
                legacy_secondary = evaluate_icd_legacy_full_n(
                    real, synth, target=target, factors=factors,
                    reference_terms=["kh2po4_pv", "urea_pv:ammonium_sulfate_pv"], lam=0.10,
                )

                fidelity_bundle = evaluate_fidelity_bundle(
                    real, synth, factors=factors, target=target, support=support
                )
                fidelity_summary = _flatten_fidelity(fidelity_bundle)
                dcr_vals = compute_dcr(real, synth, factors + [target])
                dcr_summary = summarize_dcr(dcr_vals)
                warning_messages = [
                    f"{w.category.__name__}: {str(w.message)}" for w in caught
                ]

            row: dict[str, Any] = {
                "dataset_sha256": preflight["dataset_sha256"],
                "protocol_sha256": preflight["protocol_sha256"],
                "scenario": args.scenario,
                "generator": args.generator,
                "realisation": realisation,
                "legacy_seed_label": 122 + realisation,
                "generator_seed": generator_seed,
                "generator_status": "ok",
                "synthetic_n": len(synth),
                "synthetic_hash": synth_hash,
                "ICD_primary": float(icd_primary["ICD"]),
                "S_primary": float(icd_primary["mean_S"]),
                "M_primary": float(icd_primary["mean_M"]),
                "D_primary": float(icd_primary["mean_D"]),
                "R_primary": float(icd_primary["spurious_rate"]),
                "ICD_secondary": float(icd_secondary["ICD"]),
                "S_secondary": float(icd_secondary["mean_S"]),
                "M_secondary": float(icd_secondary["mean_M"]),
                "D_secondary": float(icd_secondary["mean_D"]),
                "R_secondary": float(icd_secondary["spurious_rate"]),
                "ICD_legacy_primary": float(legacy_primary["ICD"]),
                "ICD_legacy_secondary": float(legacy_secondary["ICD"]),
                "elapsed_seconds": float(time.perf_counter() - started),
                "warnings": json.dumps(warning_messages),
                "exceptions": json.dumps([]),
                **_icd_lambda_columns("ICD_primary", icd_primary),
                **_icd_lambda_columns("ICD_secondary", icd_secondary),
                **fidelity_summary,
                **{f"dcr_{k}": float(v) for k, v in dcr_summary.items()},
            }
            if args.scenario == "sensitivity_1pct":
                cal = calibrate_response_jitter(real, target=target, percent=1.0)
                row["sensitivity_noise_seed"] = sensitivity_noise_seed(generator_seed, scenario=args.scenario)
                row["sensitivity_sigma"] = cal.sigma
                row["sensitivity_calibration_min"] = cal.real_min
                row["sensitivity_calibration_max"] = cal.real_max
            rows.append(row)

            for label, result in [("primary", icd_primary), ("secondary", icd_secondary)]:
                effects = result["effects"].copy()
                effects.insert(0, "reference_set", label)
                effects.insert(0, "realisation", realisation)
                effects.insert(0, "generator", args.generator)
                effects.insert(0, "scenario", args.scenario)
                effect_rows.append(effects)
            for label, result in [("primary", legacy_primary), ("secondary", legacy_secondary)]:
                effects = result["effects"].copy()
                effects.insert(0, "reference_set", label)
                effects.insert(0, "realisation", realisation)
                effects.insert(0, "generator", args.generator)
                effects.insert(0, "scenario", args.scenario)
                legacy_effect_rows.append(effects)

            for synthetic_row_id, d in enumerate(dcr_vals):
                dcr_rows.append({
                    "scenario": args.scenario,
                    "generator": args.generator,
                    "realisation": realisation,
                    "synthetic_row_id": synthetic_row_id,
                    "dcr": float(d),
                })

            cont = fidelity_bundle["continuous"].copy()
            cont.insert(0, "realisation", realisation)
            cont.insert(0, "generator", args.generator)
            cont.insert(0, "scenario", args.scenario)
            fidelity_cont_rows.append(cont)
            supp = fidelity_bundle["support"].copy()
            supp.insert(0, "realisation", realisation)
            supp.insert(0, "generator", args.generator)
            supp.insert(0, "scenario", args.scenario)
            fidelity_support_rows.append(supp)
            fidelity_multi_rows.append({
                "scenario": args.scenario,
                "generator": args.generator,
                "realisation": realisation,
                **fidelity_bundle["correlation"],
                **fidelity_bundle["doe"],
            })
        except Exception as exc:
            _write_json(
                outdir / f"failure_realisation_{realisation:02d}.json",
                {
                    "status": "FAIL",
                    "scientific": not smoke,
                    "generator": args.generator,
                    "scenario": args.scenario,
                    "realisation": realisation,
                    "exception": repr(exc),
                    "preflight": preflight,
                },
            )
            raise

    summary = pd.DataFrame(rows)
    expected = len(realisations)
    if len(summary) != expected:
        raise RuntimeError(f"incomplete realization set: {len(summary)} != {expected}")
    summary.to_csv(outdir / "full_realisation_manifest.csv", index=False)
    if effect_rows:
        pd.concat(effect_rows, ignore_index=True).to_csv(outdir / "icd_effects.csv", index=False)
    if legacy_effect_rows:
        pd.concat(legacy_effect_rows, ignore_index=True).to_csv(outdir / "icd_legacy_effects.csv", index=False)
    pd.DataFrame(dcr_rows).to_csv(outdir / "dcr_values.csv", index=False)
    if fidelity_cont_rows:
        pd.concat(fidelity_cont_rows, ignore_index=True).to_csv(outdir / "fidelity_univariate.csv", index=False)
    if fidelity_support_rows:
        pd.concat(fidelity_support_rows, ignore_index=True).to_csv(outdir / "fidelity_support.csv", index=False)
    pd.DataFrame(fidelity_multi_rows).to_csv(outdir / "fidelity_multivariate_doe.csv", index=False)

    _write_json(
        outdir / "completion.json",
        {
            "status": "PASS",
            "scientific": not smoke,
            "phase": "full_realisations",
            "generator": args.generator,
            "scenario": args.scenario,
            "realisations": realisations,
            "observed_realisations": int(len(summary)),
            "elapsed_seconds": time.time() - started_all,
            "preflight": preflight,
            "environment": _environment_summary(),
        },
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PEERFIX Gate 0.4 clean derivation runner")
    p.add_argument("--phase", choices=("preflight", "utility", "full_realisations"), required=True)
    p.add_argument("--generator", choices=GENERATORS)
    p.add_argument("--scenario", choices=SCENARIOS)
    p.add_argument("--geometry", choices=GEOMETRIES)
    p.add_argument("--output-dir", default="outputs/gate04")
    p.add_argument("--smoke", action="store_true", help="Non-scientific fast integration run")
    p.add_argument("--repeat-start", type=int, default=1)
    p.add_argument("--repeat-end", type=int, default=10)
    p.add_argument("--realisation-start", type=int, default=1)
    p.add_argument("--realisation-end", type=int, default=10)
    args = p.parse_args()
    if args.phase in {"utility", "full_realisations"} and (not args.generator or not args.scenario):
        p.error("--generator and --scenario are required for execution phases")
    if args.phase == "utility" and not args.geometry:
        p.error("--geometry is required for utility phase")
    if not 1 <= args.repeat_start <= args.repeat_end <= PRIMARY_N_REPEATS:
        p.error("repeat range must lie within 1..10")
    if not 1 <= args.realisation_start <= args.realisation_end <= 10:
        p.error("realisation range must lie within 1..10")
    return args


def main() -> int:
    args = parse_args()
    preflight = validate_gate04_preflight(".")
    real = pd.read_csv(preflight["dataset_path"])
    if args.phase == "preflight":
        print(json.dumps({"status": "PASS", "preflight": preflight}, indent=2))
        return 0
    if args.phase == "utility":
        run_utility(args, preflight, real)
    elif args.phase == "full_realisations":
        run_full_realisations(args, preflight, real)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
