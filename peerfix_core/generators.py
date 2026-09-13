from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Mapping

import numpy as np
import pandas as pd

from .tabddpm import SmallNTabDDPM, TabDDPMConfig


def seed_everything(seed: int) -> None:
    random.seed(int(seed))
    np.random.seed(int(seed))
    try:
        import torch
        torch.manual_seed(int(seed))
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(int(seed))
        try:
            torch.use_deterministic_algorithms(True, warn_only=True)
        except Exception:
            pass
    except Exception:
        pass


def snap_to_support(df: pd.DataFrame, support: Mapping[str, list[float]]) -> pd.DataFrame:
    """Snap only declared design-factor columns; never clip or snap the response."""
    out = df.copy()
    for col, levels in support.items():
        if col not in out.columns:
            raise KeyError(f"support column missing from synthetic output: {col}")
        allowed = np.asarray(levels, dtype=float)
        x = pd.to_numeric(out[col], errors="coerce").to_numpy(float)
        if not np.isfinite(x).all():
            raise ValueError(f"non-finite synthetic values in factor {col}")
        idx = np.abs(x[:, None] - allowed[None, :]).argmin(axis=1)
        out[col] = allowed[idx]
    return out


@dataclass(frozen=True)
class GeneratorSpec:
    name: str
    factor_support: Mapping[str, list[float]]
    ctgan_epochs: int = 300
    tvae_epochs: int = 300
    tabddpm: TabDDPMConfig = TabDDPMConfig()


def _sdv_metadata(train_df: pd.DataFrame):
    try:
        from sdv.metadata import SingleTableMetadata
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("SDV is required for Gaussian Copula/CTGAN/TVAE") from exc
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data=train_df)
    # PEERFIX derivation/adapters declare these columns numerical; factor support is
    # enforced after sampling, not through categorical coercion inside the generator.
    for col in train_df.columns:
        metadata.update_column(column_name=col, sdtype="numerical")
    metadata.validate()
    return metadata


def _try_set_model_seed(synthesizer, seed: int) -> None:
    """Best-effort explicit model RNG binding on top of global RNG seeding.

    SDV/CTGAN versions expose random-state hooks at different levels. Gate 0.3 records
    package versions and tests import/fit/sample compatibility; Gate 0.5 will verify
    repeatability on the frozen environment.
    """
    candidates = [synthesizer, getattr(synthesizer, "_model", None)]
    for obj in candidates:
        if obj is None:
            continue
        setter = getattr(obj, "set_random_state", None)
        if callable(setter):
            try:
                setter(int(seed))
                return
            except Exception:
                pass


def _sdv_generate(
    name: str,
    train_df: pd.DataFrame,
    n: int,
    seed: int,
    *,
    spec: GeneratorSpec,
    smoke: bool,
) -> pd.DataFrame:
    try:
        from sdv.single_table import (
            GaussianCopulaSynthesizer,
            CTGANSynthesizer,
            TVAESynthesizer,
        )
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("SDV is required for Gaussian Copula/CTGAN/TVAE") from exc

    seed_everything(seed)
    metadata = _sdv_metadata(train_df)
    common = dict(metadata=metadata, enforce_min_max_values=False, enforce_rounding=False)

    if name == "gaussian_copula":
        synth = GaussianCopulaSynthesizer(**common)
    elif name == "ctgan":
        kwargs = dict(common)
        kwargs.update(epochs=(2 if smoke else spec.ctgan_epochs), verbose=False)
        if smoke:
            kwargs.update(batch_size=20, cuda=False)
        synth = CTGANSynthesizer(**kwargs)
    elif name == "tvae":
        kwargs = dict(common)
        kwargs.update(epochs=(2 if smoke else spec.tvae_epochs))
        if smoke:
            kwargs.update(batch_size=20, cuda=False)
        synth = TVAESynthesizer(**kwargs)
    else:  # pragma: no cover
        raise KeyError(name)

    synth.fit(train_df)
    _try_set_model_seed(synth, seed)
    seed_everything(seed)
    out = synth.sample(num_rows=int(n))
    out = out[list(train_df.columns)].copy()
    return snap_to_support(out, spec.factor_support)


def _tabddpm_generate(
    train_df: pd.DataFrame,
    n: int,
    seed: int,
    *,
    spec: GeneratorSpec,
    smoke: bool,
) -> pd.DataFrame:
    cfg = spec.tabddpm.smoke() if smoke else spec.tabddpm
    model = SmallNTabDDPM(cfg, device="cpu" if smoke else None)
    model.fit(train_df, seed=seed)
    out = model.sample(int(n), seed=seed)
    return snap_to_support(out, spec.factor_support)


def build_generator(spec: GeneratorSpec, *, smoke: bool = False) -> Callable[[pd.DataFrame, int, int], pd.DataFrame]:
    """Return the fold-safe generator function expected by ``utility.evaluate_generator_utility``."""
    name = spec.name.lower()
    if name not in available_generators():
        raise KeyError(f"unsupported PEERFIX generator: {spec.name}")

    def generate(train_df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
        if len(train_df) < 2:
            raise ValueError("generator requires at least two real training rows")
        if name in {"gaussian_copula", "ctgan", "tvae"}:
            return _sdv_generate(name, train_df, n, seed, spec=spec, smoke=smoke)
        return _tabddpm_generate(train_df, n, seed, spec=spec, smoke=smoke)

    return generate


def available_generators() -> tuple[str, ...]:
    return ("gaussian_copula", "ctgan", "tvae", "tabddpm")
