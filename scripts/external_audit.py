from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from peerfix_core.hashing import persist_dataframe_canonical

GENERATORS = ("gaussian_copula", "ctgan", "tvae", "tabddpm")
GEOMETRIES = ("row", "grouped_condition")
EXPECTED_HASH = {
    "ext_a": "a97a23d1f1dd81ff2b8270ae235f5b2b3fbfca7d1ccd6f2e75e989c6ec23e7b9",
    "ext_b_y1": "f65bda7bebbac1d7cbaf1cf71a416465874717536640e1971c39fea850929cf7",
    "ext_b_y3": "f65bda7bebbac1d7cbaf1cf71a416465874717536640e1971c39fea850929cf7",
}
EXPECTED_N = {"ext_a": 27, "ext_b_y1": 19, "ext_b_y3": 19}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def audit(root: Path, dataset_id: str, outdir: Path) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    trtr_frames: dict[str, list[pd.DataFrame]] = {g: [] for g in GEOMETRIES}

    def check(name: str, ok: bool, detail: str = ""):
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
        if not ok:
            raise RuntimeError(f"external audit failed: {name}: {detail}")

    expected_hash = EXPECTED_HASH[dataset_id]
    expected_n = EXPECTED_N[dataset_id]

    for generator in GENERATORS:
        gbase = root / dataset_id / generator
        check(f"{generator}:root_exists", gbase.exists(), str(gbase))

        for geometry in GEOMETRIES:
            u = gbase / "utility" / geometry
            comp = _load_json(u / "completion.json")
            check(f"{generator}:{geometry}:completion", comp.get("status") == "PASS")
            metrics = pd.read_csv(u / "repeat_level_metrics.csv", float_precision="round_trip")
            manifest = pd.read_csv(u / "fold_manifest.csv", float_precision="round_trip")
            preds = pd.read_csv(u / "heldout_predictions.csv", float_precision="round_trip")
            check(f"{generator}:{geometry}:folds", len(manifest) == 50, str(len(manifest)))
            check(f"{generator}:{geometry}:metrics", len(metrics) == 40, str(len(metrics)))
            check(
                f"{generator}:{geometry}:dataset_hash",
                manifest["canonical_csv_sha256"].astype(str).nunique() == 1
                and str(manifest["canonical_csv_sha256"].iloc[0]) == expected_hash,
            )
            check(
                f"{generator}:{geometry}:generator_status",
                set(manifest["generator_status"].astype(str)) == {"ok"},
            )
            for (repeat, model, regime), grp in preds.groupby(["repeat", "model", "regime"]):
                check(
                    f"{generator}:{geometry}:coverage:r{repeat}:{model}:{regime}",
                    len(grp) == expected_n and grp["row_id"].nunique() == expected_n,
                    f"rows={len(grp)}, unique={grp['row_id'].nunique()}",
                )
            trtr = preds[preds["regime"] == "TRTR"].copy()
            trtr["generator"] = generator
            trtr_frames[geometry].append(trtr)

            lr = metrics[metrics["model"] == "lr"]
            summaries.append({
                "dataset_id": dataset_id,
                "generator": generator,
                "geometry": geometry,
                "TRTR_r2_mean": float(lr["TRTR_r2"].mean()),
                "TSTR_r2_mean": float(lr["TSTR_r2"].mean()),
                "AUGTR_r2_mean": float(lr["AUGTR_r2"].mean()),
                "delta_r2_mean": float(lr["delta_r2"].mean()),
                "augmentation_delta_r2_mean": float(lr["augmentation_delta_r2"].mean()),
            })

        f = gbase / "full"
        comp = _load_json(f / "completion.json")
        check(f"{generator}:full:completion", comp.get("status") == "PASS")
        manifest = pd.read_csv(f / "full_realisation_manifest.csv", float_precision="round_trip")
        icd = pd.read_csv(f / "icd_summary.csv", float_precision="round_trip")
        fidelity = pd.read_csv(f / "fidelity_summary.csv", float_precision="round_trip")
        check(f"{generator}:full:realisations", len(manifest) == 10, str(len(manifest)))
        check(f"{generator}:full:unique_seeds", manifest["generator_seed"].nunique() == 10)
        check(f"{generator}:full:unique_hashes", manifest["synthetic_hash"].nunique() == 10)
        check(f"{generator}:full:icd_rows", len(icd) == 10)
        check(f"{generator}:full:fidelity_rows", len(fidelity) == 10)
        for row in summaries:
            if row["generator"] == generator:
                row["ICD_mean"] = float(icd["ICD"].mean())
                row["ICD_sd"] = float(icd["ICD"].std(ddof=1))
                row["KS_mean"] = float(fidelity["ks_statistic"].mean())
                row["Wasserstein_mean"] = float(fidelity["wasserstein_distance"].mean())
                row["corr_of_corr_mean"] = float(fidelity["correlation_of_correlations"].mean())
                row["DOE_cell_coverage_mean"] = float(fidelity["factorial_cell_coverage"].mean())

    for geometry, frames in trtr_frames.items():
        all_trtr = pd.concat(frames, ignore_index=True)
        key = ["repeat", "fold", "model", "row_id"]
        pivot = all_trtr.pivot_table(index=key, columns="generator", values="y_pred", aggfunc="first")
        check(f"{geometry}:TRTR_generator_invariance", bool((pivot.max(axis=1) - pivot.min(axis=1)).abs().max() <= 1e-12))

    outdir.mkdir(parents=True, exist_ok=True)
    checks_df = pd.DataFrame(checks)
    summary_df = pd.DataFrame(summaries)
    persist_dataframe_canonical(checks_df, outdir / "audit_checks.csv")
    persist_dataframe_canonical(summary_df, outdir / "scientific_summary.csv")
    result = {
        "status": "PASS",
        "dataset_id": dataset_id,
        "checks": len(checks),
        "failed": int((checks_df["status"] != "PASS").sum()),
        "generators": list(GENERATORS),
        "geometries": list(GEOMETRIES),
        "note": "PASS denotes execution/integrity conformance; scientific transportability is interpreted from the frozen metrics without post-hoc retuning.",
    }
    (outdir / "audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--dataset", choices=sorted(EXPECTED_HASH), required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    print(json.dumps(audit(Path(args.root), args.dataset, Path(args.output_dir)), indent=2))


if __name__ == "__main__":
    main()
