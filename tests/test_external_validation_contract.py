from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

from peerfix_external.icd_design import evaluate_design_icd_matched_n


def _runner():
    path = Path("scripts/external_validation_runner.py")
    spec = importlib.util.spec_from_file_location("external_validation_runner", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_external_canonical_table_hashes_and_sizes():
    r = _runner()
    a, ca = r._load("ext_a")
    b, cb = r._load("ext_b_y1")
    assert len(a) == 27
    assert len(b) == 19
    assert ca["csv_actual_sha256"] == "a97a23d1f1dd81ff2b8270ae235f5b2b3fbfca7d1ccd6f2e75e989c6ec23e7b9"
    assert cb["csv_actual_sha256"] == "f65bda7bebbac1d7cbaf1cf71a416465874717536640e1971c39fea850929cf7"


def test_ext_a_preflight_reconstructs_source_model_and_signs():
    r = _runner()
    out = r.preflight("ext_a")
    assert out["status"] == "PASS"
    assert out["n_rows"] == 27
    assert out["unique_factor_tuples"] == 25
    assert out["modelability"]["r2"] == pytest.approx(0.94516799, abs=2e-7)
    terms = out["modelability"]["reference_terms"]
    assert terms["D"]["sign"] == "positive"
    assert terms["A:B"]["sign"] == "negative"
    assert terms["A:D"]["sign"] == "positive"
    assert terms["B:C"]["sign"] == "negative"
    assert terms["B:D"]["sign"] == "negative"


def test_ext_b_response_specific_modelability_gate():
    r = _runner()
    y1 = r.preflight("ext_b_y1")
    y2 = r.preflight("ext_b_y2")
    y3 = r.preflight("ext_b_y3")
    assert y1["status"] == "PASS"
    assert y2["status"] == "BLOCKED_BY_MODELABILITY"
    assert y3["status"] == "PASS"
    assert y1["modelability"]["reference_terms"]["X1"]["sign"] == "negative"
    assert y1["modelability"]["reference_terms"]["X1:X4"]["sign"] == "positive"
    assert y3["modelability"]["reference_terms"]["X2:X3"]["sign"] == "positive"


def test_ext_b_y2_synthetic_execution_is_fail_closed(tmp_path):
    r = _runner()
    with pytest.raises(RuntimeError, match="modelability gate"):
        r.run_utility("ext_b_y2", "gaussian_copula", "row", tmp_path)


def test_adapter_icd_handles_five_level_ccd_without_core_change():
    r = _runner()
    real, cfg = r._load("ext_a")
    synth = pd.concat([real] * 6, ignore_index=True).iloc[:140].copy()
    result = evaluate_design_icd_matched_n(
        real,
        synth,
        target="STred_mNm",
        factors=["A", "B", "C", "D"],
        reference_terms=["D", "A:B", "A:D", "B:C", "B:D"],
        include_two_way=True,
        include_quadratic=True,
        matched_n=27,
        n_subsamples=10,
        master_seed=123,
        generator="test",
        realisation=1,
    )
    assert 0.0 <= result["mean_S"] <= 1.0
    assert 0.0 <= result["mean_M"] <= 1.0
    assert 0.0 <= result["mean_D"] <= 1.0
    assert result["matched_n"] == 27
