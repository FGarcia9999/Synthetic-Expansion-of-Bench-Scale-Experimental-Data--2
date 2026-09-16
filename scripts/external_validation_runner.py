from __future__ import annotations

import argparse
import hashlib
import json
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from peerfix_core.dcr import compute_dcr, summarize_dcr
from peerfix_core.fidelity import evaluate_fidelity_bundle
from peerfix_core.generators import GeneratorSpec, build_generator
from peerfix_core.hashing import hash_dataframe, persist_dataframe_canonical, sha256_file
from peerfix_core.seeds import derive_seed
from peerfix_core.splits import repeated_group_condition_kfold, repeated_row_kfold
from peerfix_core.utility import evaluate_generator_utility
from peerfix_external.icd_design import evaluate_design_icd_matched_n, fit_design_model

MASTER_SEED = 123
N_SPLITS = 5
N_REPEATS = 10
N_SYNTHETIC = 140
N_REALISATIONS = 10
ICD_SUBSAMPLES = 1000
MODEL_PANEL = ("lr", "rf", "gbr", "mlp")
GENERATORS = ("gaussian_copula", "ctgan", "tvae", "tabddpm")
SCENARIO = "baseline_0pct"
FROZEN_CORE_COMMIT = "0d5a73d128fe374c8165f3b84a2412ac9b02cbc1"

DATASETS: dict[str, dict[str, Any]] = {
    "ext_a": {
        "csv": "data/external/ext_a_c_mogii_run_level.csv",
        "csv_sha256": "a97a23d1f1dd81ff2b8270ae235f5b2b3fbfca7d1ccd6f2e75e989c6ec23e7b9",
        "adapter": "config/external/01_ADAPTER_C_MOGII.yaml",
        "n": 27,
        "factors": ["A", "B", "C", "D"],
        "target": "STred_mNm",
        "reference_terms": ["D", "A:B", "A:D", "B:C", "B:D"],
        "include_quadratic": True,
        "modelability": "PASS",
    },
    "ext_b_y1": {
        "csv": "data/external/ext_b_c_utilis_run_level.csv",
        "csv_sha256": "f65bda7bebbac1d7cbaf1cf71a416465874717536640e1971c39fea850929cf7",
        "adapter": "config/external/02_ADAPTER_C_UTILIS.yaml",
        "n": 19,
        "factors": ["X1", "X2", "X3", "X4"],
        "target": "Y1_surface_tension_mNm",
        "reference_terms": ["X1", "X1:X4"],
        "include_quadratic": False,
        "modelability": "PASS",
    },
    "ext_b_y2": {
        "csv": "data/external/ext_b_c_utilis_run_level.csv",
        "csv_sha256": "f65bda7bebbac1d7cbaf1cf71a416465874717536640e1971c39fea850929cf7",
        "adapter": "config/external/02_ADAPTER_C_UTILIS.yaml",
        "n": 19,
        "factors": ["X1", "X2", "X3", "X4"],
        "target": "Y2_E24_motor_pct",
        "reference_terms": [],
        "include_quadratic": False,
        "modelability": "BLOCK_RELATION_IDENTIFIABILITY",
    },
    "ext_b_y3": {
        "csv": "data/external/ext_b_c_utilis_run_level.csv",
        "csv_sha256": "f65bda7bebbac1d7cbaf1cf71a416465874717536640e1971c39fea850929cf7",
        "adapter": "config/external/02_ADAPTER_C_UTILIS.yaml",
        "n": 19,
        "factors": ["X1", "X2", "X3", "X4"],
        "target": "Y3_E24_canola_pct",
        "reference_terms": ["X2:X3"],
        "include_quadratic": False,
        "modelability": "CONDITIONAL_PASS",
    },
}


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def _sha(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _config(dataset_id: str) -> dict[str, Any]:
    if dataset_id not in DATASETS:
        raise KeyError(f"unsupported external dataset/block: {dataset_id}")
    return DATASETS[dataset_id]


def _load(dataset_id: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    cfg = _config(dataset_id)
    csv_path = Path(cfg["csv"])
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)
    actual = _sha(csv_path)
    if actual != cfg["csv_sha256"]:
        raise RuntimeError(f"external canonical CSV hash mismatch: {actual} != {cfg['csv_sha256']}")
    adapter_path = Path(cfg["adapter"])
    if not adapter_path.exists():
        raise FileNotFoundError(adapter_path)
    adapter = yaml.safe_load(adapter_path.read_text(encoding="utf-8"))
    if adapter["adapter"]["frozen_core_commit"] != FROZEN_CORE_COMMIT:
        raise RuntimeError("adapter is not anchored to the frozen PEERFIX-Core commit")

    raw = pd.read_csv(csv_path, float_precision="round_trip")
    factors = list(cfg["factors"])
    target = str(cfg["target"])
    missing = [c for c in factors + [target] if c not in raw.columns]
    if missing:
        raise RuntimeError(f"external table missing required columns: {missing}")
    real = raw[factors + [target]].copy()
    if len(real) != int(cfg["n"]):
        raise RuntimeError(f"external row count mismatch: {len(real)} != {cfg['n']}")
    if real.isna().any().any():
        raise RuntimeError("external run-level table has missing factor/target values")
    return real, {**cfg, "adapter_sha256": _sha(adapter_path), "csv_actual_sha256": actual}


def _support(real: pd.DataFrame, factors: list[str]) -> dict[str, list[float]]:
    return {c: sorted(pd.to_numeric(real[c], errors="raise").astype(float).unique().tolist()) for c in factors}


def _groups(real: pd.DataFrame, factors: list[str]) -> pd.Series:
    return real[factors].astype(str).agg("|".join, axis=1)


def _splits(real: pd.DataFrame, factors: list[str], geometry: str):
    if geometry == "row":
        return list(repeated_row_kfold(len(real), n_splits=N_SPLITS, n_repeats=N_REPEATS, seed=MASTER_SEED))
    if geometry == "grouped_condition":
        return list(repeated_group_condition_kfold(_groups(real, factors), n_splits=N_SPLITS, n_repeats=N_REPEATS, master_seed=MASTER_SEED))
    raise KeyError(geometry)


def preflight(dataset_id: str) -> dict[str, Any]:
    real, cfg = _load(dataset_id)
    factors = list(cfg["factors"])
    target = str(cfg["target"])
    support = _support(real, factors)
    group_count = int(_groups(real, factors).nunique())
    if group_count < N_SPLITS:
        raise RuntimeError("insufficient unique DOE conditions for grouped 5-fold CV")

    model_summary: dict[str, Any] = {"status": cfg["modelability"]}
    if cfg["modelability"] != "BLOCK_RELATION_IDENTIFIABILITY":
        fit = fit_design_model(
            real,
            target=target,
            factors=factors,
            include_two_way=True,
            include_quadratic=bool(cfg["include_quadratic"]),
        )
        model_summary.update({
            "r2": float(fit.rsquared),
            "adj_r2": float(fit.rsquared_adj),
            "df_resid": float(fit.df_resid),
            "reference_terms": {
                term: {
                    "beta": float(fit.params[term]),
                    "p": float(fit.pvalues[term]),
                    "sign": "positive" if float(fit.params[term]) > 0 else "negative",
                }
                for term in cfg["reference_terms"]
            },
        })

    out = {
        "status": "PASS" if cfg["modelability"] != "BLOCK_RELATION_IDENTIFIABILITY" else "BLOCKED_BY_MODELABILITY",
        "dataset_id": dataset_id,
        "n_rows": int(len(real)),
        "factors": factors,
        "target": target,
        "factor_support": support,
        "unique_factor_tuples": group_count,
        "canonical_csv": cfg["csv"],
        "canonical_csv_sha256": cfg["csv_actual_sha256"],
        "adapter": cfg["adapter"],
        "adapter_sha256": cfg["adapter_sha256"],
        "frozen_core_commit": FROZEN_CORE_COMMIT,
        "modelability": model_summary,
    }
    return out


def run_utility(dataset_id: str, generator: str, geometry: str, outdir: Path) -> None:
    real, cfg = _load(dataset_id)
    if cfg["modelability"] == "BLOCK_RELATION_IDENTIFIABILITY":
        raise RuntimeError(f"synthetic execution prohibited by modelability gate for {dataset_id}")
    factors = list(cfg["factors"])
    target = str(cfg["target"])
    support = _support(real, factors)
    spec = GeneratorSpec(name=generator, factor_support=support)
    generator_fn = build_generator(spec, smoke=False)
    splits = _splits(real, factors, geometry)
    started = time.time()
    metrics, manifest, preds = evaluate_generator_utility(
        real,
        target=target,
        splits=splits,
        generator_name=generator,
        generator_fn=generator_fn,
        n_synthetic=N_SYNTHETIC,
        master_seed=MASTER_SEED,
        scenario=SCENARIO,
        model_names=MODEL_PANEL,
        return_predictions=True,
    )
    if len(manifest) != N_SPLITS * N_REPEATS:
        raise RuntimeError("incomplete external utility fold set")
    metrics.insert(0, "dataset_id", dataset_id)
    metrics.insert(1, "geometry", geometry)
    manifest.insert(0, "dataset_id", dataset_id)
    manifest.insert(1, "geometry", geometry)
    manifest.insert(2, "canonical_csv_sha256", cfg["csv_actual_sha256"])
    preds.insert(0, "dataset_id", dataset_id)
    preds.insert(1, "geometry", geometry)
    outdir.mkdir(parents=True, exist_ok=True)
    persist_dataframe_canonical(metrics, outdir / "repeat_level_metrics.csv")
    persist_dataframe_canonical(manifest, outdir / "fold_manifest.csv")
    persist_dataframe_canonical(preds, outdir / "heldout_predictions.csv")
    _write_json(outdir / "completion.json", {
        "status": "PASS", "phase": "utility", "dataset_id": dataset_id,
        "generator": generator, "geometry": geometry, "elapsed_seconds": time.time() - started,
        "canonical_csv_sha256": cfg["csv_actual_sha256"], "frozen_core_commit": FROZEN_CORE_COMMIT,
    })


def run_full(dataset_id: str, generator: str, outdir: Path) -> None:
    real, cfg = _load(dataset_id)
    if cfg["modelability"] == "BLOCK_RELATION_IDENTIFIABILITY":
        raise RuntimeError(f"synthetic execution prohibited by modelability gate for {dataset_id}")
    factors = list(cfg["factors"])
    target = str(cfg["target"])
    support = _support(real, factors)
    spec = GeneratorSpec(name=generator, factor_support=support)
    generator_fn = build_generator(spec, smoke=False)
    synth_dir = outdir / "synthetic_realisations"
    synth_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, Any]] = []
    fidelity_rows: list[dict[str, Any]] = []
    dcr_rows: list[dict[str, Any]] = []
    icd_rows: list[dict[str, Any]] = []
    effect_frames: list[pd.DataFrame] = []
    started_all = time.time()

    for realisation in range(1, N_REALISATIONS + 1):
        seed = derive_seed(MASTER_SEED, purpose="generator_full", scenario=SCENARIO, generator=generator, realisation=realisation)
        started = time.perf_counter()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            synth = generator_fn(real, N_SYNTHETIC, seed)
        synth_path = synth_dir / f"realisation_{realisation:02d}.csv"
        synth_hash = persist_dataframe_canonical(synth, synth_path)

        bundle = evaluate_fidelity_bundle(real, synth, factors=factors, target=target, support=support)
        continuous = bundle["continuous"].iloc[0]
        support_df = bundle["support"]
        corr = bundle["correlation"]
        doe = bundle["doe"]
        fidelity_rows.append({
            "dataset_id": dataset_id, "generator": generator, "realisation": realisation,
            "ks_statistic": float(continuous["ks_statistic"]),
            "wasserstein_distance": float(continuous["wasserstein_distance"]),
            "mean_factor_support_coverage": float(support_df["support_coverage"].mean()),
            "mean_factor_tvd": float(support_df["total_variation_distance"].mean()),
            "max_off_support_fraction": float(support_df["off_support_fraction"].max()),
            **{k: float(v) for k, v in corr.items()}, **{k: float(v) for k, v in doe.items()},
        })
        dcr = compute_dcr(real, synth, factors + [target])
        dcr_rows.append({"dataset_id": dataset_id, "generator": generator, "realisation": realisation, **summarize_dcr(dcr)})

        icd = evaluate_design_icd_matched_n(
            real, synth, target=target, factors=factors, reference_terms=cfg["reference_terms"],
            include_two_way=True, include_quadratic=bool(cfg["include_quadratic"]),
            matched_n=len(real), n_subsamples=ICD_SUBSAMPLES, alpha=0.05, lam=0.10,
            master_seed=MASTER_SEED, scenario=SCENARIO, generator=generator, realisation=realisation,
        )
        icd_rows.append({
            "dataset_id": dataset_id, "generator": generator, "realisation": realisation,
            "ICD": float(icd["ICD"]), "mean_S": float(icd["mean_S"]),
            "mean_M": float(icd["mean_M"]), "mean_D": float(icd["mean_D"]),
            "spurious_rate": float(icd["spurious_rate"]), "matched_n": int(icd["matched_n"]),
        })
        ef = icd["effects"].copy()
        ef.insert(0, "dataset_id", dataset_id); ef.insert(1, "generator", generator); ef.insert(2, "realisation", realisation)
        effect_frames.append(ef)
        manifest_rows.append({
            "dataset_id": dataset_id, "generator": generator, "realisation": realisation,
            "generator_seed": int(seed), "synthetic_n": int(len(synth)), "synthetic_hash": synth_hash,
            "elapsed_seconds": float(time.perf_counter() - started),
            "warnings": json.dumps([f"{w.category.__name__}: {w.message}" for w in caught]),
            "generator_status": "ok", "canonical_csv_sha256": cfg["csv_actual_sha256"],
            "frozen_core_commit": FROZEN_CORE_COMMIT,
        })

    outdir.mkdir(parents=True, exist_ok=True)
    manifest = pd.DataFrame(manifest_rows)
    if manifest["generator_seed"].nunique() != N_REALISATIONS or manifest["synthetic_hash"].nunique() != N_REALISATIONS:
        raise RuntimeError("external full-realisation seed/hash uniqueness contract failed")
    persist_dataframe_canonical(manifest, outdir / "full_realisation_manifest.csv")
    persist_dataframe_canonical(pd.DataFrame(fidelity_rows), outdir / "fidelity_summary.csv")
    persist_dataframe_canonical(pd.DataFrame(dcr_rows), outdir / "dcr_summary.csv")
    persist_dataframe_canonical(pd.DataFrame(icd_rows), outdir / "icd_summary.csv")
    persist_dataframe_canonical(pd.concat(effect_frames, ignore_index=True), outdir / "icd_effects.csv")
    _write_json(outdir / "completion.json", {
        "status": "PASS", "phase": "full_realisations", "dataset_id": dataset_id,
        "generator": generator, "realisations": N_REALISATIONS,
        "unique_generator_seeds": int(manifest["generator_seed"].nunique()),
        "unique_synthetic_hashes": int(manifest["synthetic_hash"].nunique()),
        "elapsed_seconds": time.time() - started_all, "canonical_csv_sha256": cfg["csv_actual_sha256"],
        "frozen_core_commit": FROZEN_CORE_COMMIT,
    })


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["preflight", "utility", "full"], required=True)
    ap.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    ap.add_argument("--generator", choices=GENERATORS)
    ap.add_argument("--geometry", choices=["row", "grouped_condition"])
    ap.add_argument("--output-dir", default="outputs/external")
    args = ap.parse_args()
    if args.phase == "preflight":
        print(json.dumps(preflight(args.dataset), indent=2, ensure_ascii=False))
        return
    if not args.generator:
        ap.error("--generator is required for utility/full")
    outdir = Path(args.output_dir)
    if args.phase == "utility":
        if not args.geometry:
            ap.error("--geometry is required for utility")
        run_utility(args.dataset, args.generator, args.geometry, outdir)
    else:
        run_full(args.dataset, args.generator, outdir)


if __name__ == "__main__":
    main()
