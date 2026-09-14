from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from peerfix_core.tabddpm import (
    SmallNTabDDPM,
    TabDDPMConfig,
    _weighted_denoising_mse,
)


def _toy_df() -> pd.DataFrame:
    # Factor has <=6 unique values and must not receive bootstrap jitter.
    # Target has >6 unique values and remains eligible for the historical light jitter.
    return pd.DataFrame(
        {
            "factor": [0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
            "target": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0],
        }
    )


def test_predeclared_timestep_weighting_is_enabled_and_matches_historical_formula():
    cfg = TabDDPMConfig()
    assert cfg.timestep_loss_weighting is True

    pred = torch.zeros((2, 2), dtype=torch.float32)
    eps = torch.ones((2, 2), dtype=torch.float32)
    abar = torch.tensor([1.0, 0.25], dtype=torch.float32)

    observed = _weighted_denoising_mse(pred, eps, abar, enabled=True)
    expected = torch.mean((1.0 / torch.sqrt(abar + 1e-8)).unsqueeze(-1) * torch.ones_like(pred))
    assert torch.allclose(observed, expected)

    plain = _weighted_denoising_mse(pred, eps, abar, enabled=False)
    assert torch.allclose(plain, torch.tensor(1.0))


def test_bootstrap_jitter_is_discrete_aware_but_retains_target_jitter():
    df = _toy_df()
    cfg = TabDDPMConfig(bootstrap_augment=True, bootstrap_factor=4, bootstrap_noise_std=0.05)
    model = SmallNTabDDPM(cfg, device="cpu")
    model.discrete_mask = model._detect_discrete_mask(df)

    assert model.discrete_mask.tolist() == [True, False]

    z = df.to_numpy(dtype=np.float32)
    out = model._augment(z, np.random.default_rng(123))

    # No Gaussian jitter may be added to the DOE-like factor column.
    assert set(np.unique(out[:, 0])).issubset({0.0, 1.0})

    # The continuous target retains the historical light bootstrap jitter.
    original_target = set(df["target"].tolist())
    assert any(float(v) not in original_target for v in out[:, 1])


def test_reverse_process_uses_posterior_variance_and_sampling_is_seeded():
    df = _toy_df()
    cfg = TabDDPMConfig(
        epochs=2,
        timesteps=8,
        batch_size=8,
        hidden_dim=16,
        n_layers=1,
        dropout=0.0,
        bootstrap_augment=False,
        patience=2,
        scheduler_patience=1,
        timestep_loss_weighting=True,
    )
    model = SmallNTabDDPM(cfg, device="cpu").fit(df, seed=1729)

    assert model.posterior_variance is not None
    assert model.alpha_bar is not None
    assert model.alpha_bar_prev is not None
    assert model.betas is not None

    expected = model.betas * (1.0 - model.alpha_bar_prev) / torch.clamp(
        1.0 - model.alpha_bar, min=1e-12
    )
    expected = torch.clamp(expected, min=0.0)
    assert torch.allclose(model.posterior_variance, expected)
    assert torch.isclose(model.posterior_variance[0], torch.tensor(0.0), atol=1e-8)

    same_a = model.sample(6, seed=99)
    same_b = model.sample(6, seed=99)
    different = model.sample(6, seed=100)
    assert np.allclose(same_a.to_numpy(), same_b.to_numpy())
    assert not np.allclose(same_a.to_numpy(), different.to_numpy())


def test_inverse_transform_is_not_clipped_to_training_range():
    df = _toy_df()
    cfg = TabDDPMConfig(
        epochs=1,
        timesteps=4,
        batch_size=8,
        hidden_dim=8,
        n_layers=1,
        dropout=0.0,
        bootstrap_augment=False,
        patience=1,
        scheduler_patience=1,
    )
    model = SmallNTabDDPM(cfg, device="cpu").fit(df, seed=7)

    # A deliberately extreme latent value must remain extreme after inverse scaling;
    # no train-range clipping is allowed by the Gate 0.4 contract.
    extreme = np.full((1, 2), 20.0, dtype=np.float32)
    restored = model._normalize_inverse(extreme)
    assert restored[0, 1] > float(df["target"].max())
