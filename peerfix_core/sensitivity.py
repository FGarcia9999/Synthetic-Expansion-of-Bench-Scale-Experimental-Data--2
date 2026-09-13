from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from .seeds import derive_seed


GeneratorFn = Callable[[pd.DataFrame, int, int], pd.DataFrame]


@dataclass(frozen=True)
class ResponseJitterCalibration:
    target: str
    percent: float
    real_min: float
    real_max: float
    real_range: float
    sigma: float


def calibrate_response_jitter(
    real_calibration_df: pd.DataFrame,
    *,
    target: str,
    percent: float = 1.0,
) -> ResponseJitterCalibration:
    """Calibrate the historical PEERFIX response-jitter sensitivity.

    The calibration dataset is explicit. During utility validation it MUST be the
    real training fold only. The historical implementation identified DOE-factor
    columns as discrete (<=6 observed levels), so for PEERFIX2 the perturbation
    effectively acted on the continuous surface-tension response. The clean Core
    makes that intent explicit instead of inferring column roles from cardinality.

    ``percent=1.0`` means sigma = 1% of the response range in the calibration data.
    """
    if target not in real_calibration_df.columns:
        raise KeyError(target)
    if percent < 0:
        raise ValueError("percent must be non-negative")

    y = pd.to_numeric(real_calibration_df[target], errors="coerce").to_numpy(float)
    y = y[np.isfinite(y)]
    if y.size < 2:
        raise ValueError("response-jitter calibration requires at least two finite real values")

    lo = float(np.min(y))
    hi = float(np.max(y))
    span = float(hi - lo)
    sigma = float((percent / 100.0) * span)
    return ResponseJitterCalibration(
        target=target,
        percent=float(percent),
        real_min=lo,
        real_max=hi,
        real_range=span,
        sigma=sigma,
    )


def sensitivity_noise_seed(generator_seed: int, *, scenario: str = "sensitivity_1pct") -> int:
    """Derive a deterministic perturbation seed without consuming generator RNG state."""
    return derive_seed(
        int(generator_seed),
        purpose="response_jitter",
        scenario=scenario,
    )


def apply_response_jitter(
    synthetic_df: pd.DataFrame,
    real_calibration_df: pd.DataFrame,
    *,
    target: str,
    percent: float = 1.0,
    seed: int,
) -> pd.DataFrame:
    """Apply deterministic Gaussian response jitter calibrated on real data only.

    Scientific boundary for PEERFIX-Core v1 pre-freeze:
    - only the declared continuous response is perturbed;
    - declared DOE factor columns are left exactly unchanged;
    - sigma is ``percent`` of the response range in ``real_calibration_df``;
    - no clipping to the observed real response range is performed;
    - no held-out real observations may be supplied during utility validation.

    The last rule is enforced by the caller/runner because this function cannot know
    whether its calibration dataframe came from a training or held-out partition.
    """
    if target not in synthetic_df.columns:
        raise KeyError(target)
    if percent == 0:
        return synthetic_df.copy()

    calibration = calibrate_response_jitter(
        real_calibration_df,
        target=target,
        percent=percent,
    )
    out = synthetic_df.copy()
    y = pd.to_numeric(out[target], errors="coerce").to_numpy(float)
    if not np.isfinite(y).all():
        raise ValueError(f"non-finite synthetic values in response {target}")

    if calibration.sigma == 0.0:
        return out

    rng = np.random.default_rng(int(seed))
    out[target] = y + rng.normal(loc=0.0, scale=calibration.sigma, size=len(out))
    return out


def wrap_generator_with_response_jitter(
    base_generator: GeneratorFn,
    *,
    target: str,
    percent: float = 1.0,
    scenario: str = "sensitivity_1pct",
) -> GeneratorFn:
    """Wrap a fold-safe generator with training-calibrated response sensitivity.

    ``utility.evaluate_generator_utility`` passes only the real training fold into
    generator functions. Therefore the wrapper inherits the no-leakage boundary:
    sensitivity calibration sees the same training fold and no held-out real rows.
    """

    def generate(train_df: pd.DataFrame, n: int, generator_seed: int) -> pd.DataFrame:
        synth = base_generator(train_df, n, generator_seed)
        noise_seed = sensitivity_noise_seed(generator_seed, scenario=scenario)
        return apply_response_jitter(
            synth,
            train_df,
            target=target,
            percent=percent,
            seed=noise_seed,
        )

    return generate
