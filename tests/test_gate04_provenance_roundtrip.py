from __future__ import annotations

from pathlib import Path

import pandas as pd

from peerfix_core.hashing import (
    hash_dataframe,
    persist_dataframe_canonical,
    read_dataframe_canonical,
    sha256_file,
)
from peerfix_core.provenance import prediction_manifest_from_dataframe


def test_dataframe_persistence_hash_roundtrip(tmp_path: Path):
    df = pd.DataFrame({
        "a": [0.1, 1.0 / 3.0, 123456.78901234567],
        "b": [42.22, 49.21, -0.000000000123456789],
    })
    path = tmp_path / "x.csv"
    digest = persist_dataframe_canonical(df, path)
    assert digest == hash_dataframe(df)
    assert digest == sha256_file(path)
    reloaded = read_dataframe_canonical(path)
    assert hash_dataframe(reloaded) == digest


def test_prediction_hashes_are_reconstructible_after_persistence(tmp_path: Path):
    preds = pd.DataFrame({
        "scenario": ["baseline_0pct"] * 4,
        "generator": ["gaussian_copula"] * 4,
        "repeat": [1] * 4,
        "fold": [1] * 4,
        "model": ["lr"] * 4,
        "regime": ["TRTR", "TRTR", "TSTR", "TSTR"],
        "row_id": [0, 1, 0, 1],
        "y_true": [42.22, 53.57, 42.22, 53.57],
        "y_pred": [45.123456789012345, 49.987654321098765, 44.111111111111114, 50.22222222222222],
        "model_seed": [1234] * 4,
    })
    path = tmp_path / "heldout_predictions.csv"
    persist_dataframe_canonical(preds, path)
    first = prediction_manifest_from_dataframe(preds)
    second = prediction_manifest_from_dataframe(read_dataframe_canonical(path))
    assert first.equals(second)
