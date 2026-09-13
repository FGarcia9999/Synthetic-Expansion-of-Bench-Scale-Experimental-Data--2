from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from peerfix_core.protocol import (
    combined_protocol_sha256,
    validate_gate04_preflight,
)


def test_gate04_repo_preflight_passes_on_authorized_state():
    result = validate_gate04_preflight(".")
    assert result["status"] == "PASS"
    assert result["protocol_label"] == "PEERFIX_CORE_v1.0_PRE_FREEZE_REV3"
    assert result["dataset_sha256"] == "c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07"
    assert result["n_rows"] == 20
    assert result["target"] == "surface_tension_mNm"
    assert len(result["protocol_sha256"]) == 64


def test_combined_protocol_hash_is_order_sensitive(tmp_path: Path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text("a: 1\n", encoding="utf-8")
    b.write_text("b: 2\n", encoding="utf-8")
    assert combined_protocol_sha256(a, b) != combined_protocol_sha256(b, a)


def test_preflight_fails_if_dataset_bytes_change(tmp_path: Path):
    # Build a minimal fake repository by copying the real protocol pair and dataset,
    # then alter one response value without changing the expected protocol hash field.
    root = tmp_path
    (root / "config").mkdir()
    (root / "data" / "derivation").mkdir(parents=True)

    for rel in [
        "config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV2.yaml",
        "config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV3_AMENDMENT.yaml",
        "data/derivation/peerfix2_historical_manuscript_dataset.csv",
    ]:
        src = Path(rel)
        dst = root / rel
        dst.write_bytes(src.read_bytes())

    p = root / "data/derivation/peerfix2_historical_manuscript_dataset.csv"
    df = pd.read_csv(p)
    df.loc[0, "surface_tension_mNm"] += 0.01
    df.to_csv(p, index=False)

    with pytest.raises(RuntimeError, match="hash mismatch"):
        validate_gate04_preflight(root)
