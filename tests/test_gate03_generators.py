from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from peerfix_core.generators import GeneratorSpec, available_generators, build_generator
from peerfix_core.tabddpm import TabDDPMConfig

DATA = Path("data/derivation/peerfix2_historical_manuscript_dataset.csv")
FACTORS = ["seawater_vv", "urea_pv", "ammonium_sulfate_pv", "kh2po4_pv"]
TARGET = "surface_tension_mNm"
SUPPORT = {
    "seawater_vv": [0.0, 50.0, 100.0],
    "urea_pv": [0.0, 0.25, 0.5],
    "ammonium_sulfate_pv": [0.2, 0.4, 0.6],
    "kh2po4_pv": [0.5, 1.0, 1.5],
}


def _spec(name: str) -> GeneratorSpec:
    return GeneratorSpec(
        name=name,
        factor_support=SUPPORT,
        tabddpm=TabDDPMConfig(
            epochs=150,
            timesteps=100,
            batch_size=32,
            learning_rate=5e-4,
            hidden_dim=128,
            n_layers=2,
            dropout=0.15,
            weight_decay=0.01,
            gradient_clip=0.5,
            patience=25,
            min_delta=5e-5,
            scheduler_patience=10,
            scheduler_factor=0.7,
            bootstrap_augment=True,
            bootstrap_factor=3,
            bootstrap_noise_std=0.01,
            robust_normalization=True,
        ),
    )


def test_exact_generator_panel_is_exposed():
    assert available_generators() == ("gaussian_copula", "ctgan", "tvae", "tabddpm")


@pytest.mark.parametrize("name", ["gaussian_copula", "ctgan", "tvae", "tabddpm"])
def test_real_generator_fit_sample_smoke(name: str):
    real = pd.read_csv(DATA)
    assert len(real) == 20
    generator = build_generator(_spec(name), smoke=True)
    out = generator(real, 12, 1729)

    assert isinstance(out, pd.DataFrame)
    assert out.shape == (12, real.shape[1])
    assert list(out.columns) == list(real.columns)
    assert np.isfinite(out.to_numpy(dtype=float)).all()

    for factor in FACTORS:
        observed = set(pd.to_numeric(out[factor]).astype(float).tolist())
        assert observed.issubset(set(SUPPORT[factor]))

    # The pre-freeze contract deliberately does not clip the response to the real
    # training range. The smoke test checks only that a finite response is delivered.
    assert np.isfinite(pd.to_numeric(out[TARGET]).to_numpy(float)).all()


def test_gaussian_copula_sampling_seed_is_reproducible_and_distinct():
    """Regression guard for the Gate 0.4 run-1 SDV fixed-seed defect.

    The same requested seed must reproduce the same Gaussian-Copula sample, while
    a different requested seed must change the sample. This specifically catches
    SDV silently reinstalling its built-in fixed sampling seed when the synthesizer
    level `_random_state_set` flag has not been bound correctly.
    """
    real = pd.read_csv(DATA)
    generator = build_generator(_spec("gaussian_copula"), smoke=True)

    a = generator(real, 40, 1729)
    b = generator(real, 40, 1729)
    c = generator(real, 40, 1730)

    pd.testing.assert_frame_equal(a, b, check_exact=True)
    assert not a.equals(c)
