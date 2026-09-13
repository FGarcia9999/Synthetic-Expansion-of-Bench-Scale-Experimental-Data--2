from __future__ import annotations

import numpy as np
import pandas as pd

from peerfix_core.sensitivity import (
    apply_response_jitter,
    calibrate_response_jitter,
    sensitivity_noise_seed,
    wrap_generator_with_response_jitter,
)


def _train() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "factor_a": [0.0, 1.0, 0.0, 1.0],
            "factor_b": [10.0, 10.0, 20.0, 20.0],
            "surface_tension_mNm": [40.0, 42.0, 48.0, 50.0],
        }
    )


def test_calibration_is_one_percent_of_explicit_training_range():
    cal = calibrate_response_jitter(
        _train(), target="surface_tension_mNm", percent=1.0
    )
    assert cal.real_min == 40.0
    assert cal.real_max == 50.0
    assert cal.real_range == 10.0
    assert cal.sigma == 0.1


def test_response_jitter_is_deterministic_and_preserves_factors():
    train = _train()
    synth = pd.DataFrame(
        {
            "factor_a": [0.0, 1.0, 1.0],
            "factor_b": [10.0, 20.0, 10.0],
            "surface_tension_mNm": [44.0, 45.0, 46.0],
        }
    )
    a = apply_response_jitter(
        synth,
        train,
        target="surface_tension_mNm",
        percent=1.0,
        seed=1234,
    )
    b = apply_response_jitter(
        synth,
        train,
        target="surface_tension_mNm",
        percent=1.0,
        seed=1234,
    )
    c = apply_response_jitter(
        synth,
        train,
        target="surface_tension_mNm",
        percent=1.0,
        seed=1235,
    )
    pd.testing.assert_frame_equal(a, b)
    pd.testing.assert_series_equal(a["factor_a"], synth["factor_a"])
    pd.testing.assert_series_equal(a["factor_b"], synth["factor_b"])
    assert not np.allclose(a["surface_tension_mNm"], c["surface_tension_mNm"])


def test_response_is_not_clipped_to_training_range():
    train = _train()
    synth = pd.DataFrame(
        {
            "factor_a": [0.0],
            "factor_b": [10.0],
            "surface_tension_mNm": [80.0],
        }
    )
    out = apply_response_jitter(
        synth,
        train,
        target="surface_tension_mNm",
        percent=1.0,
        seed=77,
    )
    assert float(out.loc[0, "surface_tension_mNm"]) > 50.0


def test_zero_percent_is_exact_noop_copy():
    train = _train()
    synth = train.iloc[:2].copy()
    out = apply_response_jitter(
        synth,
        train,
        target="surface_tension_mNm",
        percent=0.0,
        seed=1,
    )
    pd.testing.assert_frame_equal(out, synth)
    assert out is not synth


def test_wrapper_calibrates_only_on_train_argument():
    train = _train()
    seen = {}

    def base_generator(train_df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
        seen["rows"] = len(train_df)
        idx = np.arange(n) % len(train_df)
        return train_df.iloc[idx].reset_index(drop=True).copy()

    wrapped = wrap_generator_with_response_jitter(
        base_generator,
        target="surface_tension_mNm",
        percent=1.0,
    )
    out = wrapped(train.iloc[:3].copy(), 7, 555)
    assert seen["rows"] == 3
    assert len(out) == 7
    # Calibration range must be 40..48 (8 units), not any external/held-out value.
    cal = calibrate_response_jitter(
        train.iloc[:3], target="surface_tension_mNm", percent=1.0
    )
    assert cal.sigma == 0.08


def test_noise_seed_is_stable_and_separate_from_generator_seed():
    a = sensitivity_noise_seed(987, scenario="sensitivity_1pct")
    b = sensitivity_noise_seed(987, scenario="sensitivity_1pct")
    c = sensitivity_noise_seed(988, scenario="sensitivity_1pct")
    assert a == b
    assert a != c
    assert a != 987
