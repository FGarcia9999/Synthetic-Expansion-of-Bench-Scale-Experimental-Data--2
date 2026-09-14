from __future__ import annotations

from pathlib import Path

import pandas as pd

from .hashing import (
    hash_dataframe,
    persist_dataframe_canonical,
    read_dataframe_canonical,
    sha256_file,
)


PREDICTION_KEYS = ["scenario", "generator", "repeat", "fold", "model", "regime"]
PREDICTION_VALUE_COLUMNS = ["row_id", "y_true", "y_pred", "model_seed"]


def prediction_manifest_from_dataframe(preds: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key, g in preds.groupby(PREDICTION_KEYS, sort=True):
        g2 = g.sort_values("row_id")[PREDICTION_VALUE_COLUMNS].reset_index(drop=True)
        row = dict(zip(PREDICTION_KEYS, key))
        row["downstream_seed"] = int(g2["model_seed"].iloc[0])
        row["predictions_hash"] = hash_dataframe(g2)
        row["n_predictions"] = int(len(g2))
        rows.append(row)
    return pd.DataFrame(rows)


def canonicalize_csv_roundtrip(path: str | Path) -> tuple[pd.DataFrame, str]:
    """Canonicalize a persisted CSV and prove byte/hash/reload agreement."""
    path = Path(path)
    df = read_dataframe_canonical(path)
    digest = persist_dataframe_canonical(df, path)
    if sha256_file(path) != digest:
        raise RuntimeError(f"persisted byte hash mismatch: {path}")
    reloaded = read_dataframe_canonical(path)
    if hash_dataframe(reloaded) != digest:
        raise RuntimeError(f"reload canonical hash mismatch: {path}")
    return reloaded, digest


def finalize_utility_directory(path: str | Path) -> dict[str, object]:
    path = Path(path)
    required = [
        "repeat_level_metrics.csv",
        "fold_manifest.csv",
        "heldout_predictions.csv",
        "prediction_manifest.csv",
        "completion.json",
    ]
    missing = [name for name in required if not (path / name).exists()]
    if missing:
        raise RuntimeError(f"missing utility artifacts in {path}: {missing}")

    canonicalize_csv_roundtrip(path / "repeat_level_metrics.csv")
    canonicalize_csv_roundtrip(path / "fold_manifest.csv")
    preds, preds_file_hash = canonicalize_csv_roundtrip(path / "heldout_predictions.csv")

    manifest = prediction_manifest_from_dataframe(preds)
    persist_dataframe_canonical(manifest, path / "prediction_manifest.csv")
    manifest_reload = read_dataframe_canonical(path / "prediction_manifest.csv")
    regenerated = prediction_manifest_from_dataframe(read_dataframe_canonical(path / "heldout_predictions.csv"))
    if not manifest_reload.equals(regenerated):
        raise RuntimeError(f"prediction manifest round-trip mismatch: {path}")

    return {
        "path": str(path),
        "heldout_predictions_sha256": preds_file_hash,
        "prediction_groups": int(len(manifest_reload)),
        "status": "PASS",
    }


def finalize_full_realisations_directory(path: str | Path) -> dict[str, object]:
    path = Path(path)
    manifest_path = path / "full_realisation_manifest.csv"
    if not manifest_path.exists():
        raise RuntimeError(f"missing full-realisation manifest: {path}")
    manifest = read_dataframe_canonical(manifest_path)
    if len(manifest) == 0:
        raise RuntimeError(f"empty full-realisation manifest: {path}")

    hashes: dict[int, str] = {}
    for realisation in manifest["realisation"].astype(int).tolist():
        synth_path = path / "synthetic_realisations" / f"realisation_{realisation:02d}.csv"
        _, digest = canonicalize_csv_roundtrip(synth_path)
        hashes[int(realisation)] = digest

    manifest["synthetic_hash"] = manifest["realisation"].astype(int).map(hashes)
    persist_dataframe_canonical(manifest, manifest_path)
    manifest_reload = read_dataframe_canonical(manifest_path)
    for _, row in manifest_reload.iterrows():
        r = int(row["realisation"])
        synth_path = path / "synthetic_realisations" / f"realisation_{r:02d}.csv"
        if str(row["synthetic_hash"]) != sha256_file(synth_path):
            raise RuntimeError(f"synthetic manifest/file hash mismatch: {synth_path}")

    for name in [
        "dcr_values.csv",
        "fidelity_multivariate_doe.csv",
        "fidelity_support.csv",
        "fidelity_univariate.csv",
        "icd_effects.csv",
        "icd_legacy_effects.csv",
    ]:
        p = path / name
        if p.exists():
            canonicalize_csv_roundtrip(p)

    return {
        "path": str(path),
        "realisations": int(len(manifest_reload)),
        "unique_synthetic_hashes": int(manifest_reload["synthetic_hash"].nunique()),
        "status": "PASS",
    }
