from __future__ import annotations

import numpy as np
import pandas as pd

from peerfix_core.fidelity import (
    continuous_univariate_fidelity,
    correlation_fidelity,
    designed_support_fidelity,
    doe_structure_fidelity,
    evaluate_fidelity_bundle,
)


def _real() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "a": [0.0, 0.0, 1.0, 1.0],
            "b": [0.0, 1.0, 0.0, 1.0],
            "y": [10.0, 12.0, 14.0, 16.0],
        }
    )


def test_identical_data_have_zero_univariate_distance_and_full_support():
    real = _real()
    uni = continuous_univariate_fidelity(real, real.copy(), ["y"])
    assert float(uni.loc[0, "ks_statistic"]) == 0.0
    assert float(uni.loc[0, "wasserstein_distance"]) == 0.0

    support = designed_support_fidelity(real, real.copy(), {"a": [0.0, 1.0], "b": [0.0, 1.0]})
    assert np.allclose(support["support_coverage"], 1.0)
    assert np.allclose(support["total_variation_distance"], 0.0)
    assert np.allclose(support["off_support_fraction"], 0.0)


def test_doe_structure_reports_off_design_cells_without_filtering():
    real = _real()
    synth = pd.DataFrame(
        {
            "a": [0.0, 0.0, 0.5, 1.0],
            "b": [0.0, 1.0, 0.5, 1.0],
            "y": [10.0, 12.0, 13.0, 16.0],
        }
    )
    res = doe_structure_fidelity(real, synth, ["a", "b"])
    assert res["factorial_cell_coverage"] == 0.75
    assert res["off_design_cell_fraction"] == 0.25
    assert res["factor_level_frequency_deviation"] >= 0.0


def test_correlation_fidelity_is_exact_for_identical_frames():
    real = _real()
    res = correlation_fidelity(real, real.copy(), ["a", "b", "y"])
    assert np.isclose(res["correlation_of_correlations"], 1.0)
    assert np.isclose(res["frobenius_norm_correlation_difference"], 0.0)


def test_bundle_exposes_protocol_metric_families():
    real = _real()
    bundle = evaluate_fidelity_bundle(
        real,
        real.copy(),
        factors=["a", "b"],
        target="y",
        support={"a": [0.0, 1.0], "b": [0.0, 1.0]},
    )
    assert set(bundle) == {"continuous", "support", "correlation", "doe"}
