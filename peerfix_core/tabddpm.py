from __future__ import annotations

from dataclasses import dataclass, replace
import math
import random
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, StandardScaler

try:
    import torch
    import torch.nn as nn
except Exception:  # pragma: no cover - explicit dependency checked by Gate 0.3
    torch = None
    nn = None


DISCRETE_MAX_UNIQUE = 6


@dataclass(frozen=True)
class TabDDPMConfig:
    epochs: int = 150
    timesteps: int = 100
    batch_size: int = 32
    learning_rate: float = 5e-4
    hidden_dim: int = 128
    n_layers: int = 2
    dropout: float = 0.15
    weight_decay: float = 0.01
    gradient_clip: float = 0.5
    patience: int = 25
    min_delta: float = 5e-5
    scheduler_patience: int = 10
    scheduler_factor: float = 0.7
    bootstrap_augment: bool = True
    bootstrap_factor: int = 3
    bootstrap_noise_std: float = 0.01
    robust_normalization: bool = True
    timestep_loss_weighting: bool = True

    def smoke(self) -> "TabDDPMConfig":
        return replace(
            self,
            epochs=min(self.epochs, 2),
            timesteps=min(self.timesteps, 20),
            patience=2,
            scheduler_patience=1,
        )


def _seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        try:
            torch.use_deterministic_algorithms(True, warn_only=True)
        except Exception:
            pass


def _cosine_betas(timesteps: int, s: float = 0.008) -> np.ndarray:
    """Nichol-Dhariwal cosine schedule, clipped for numerical stability."""
    x = np.linspace(0, timesteps, timesteps + 1, dtype=np.float64)
    a_bar = np.cos(((x / timesteps) + s) / (1 + s) * math.pi / 2) ** 2
    a_bar = a_bar / a_bar[0]
    betas = 1.0 - (a_bar[1:] / a_bar[:-1])
    return np.clip(betas, 1e-5, 0.999).astype(np.float32)


def _weighted_denoising_mse(
    pred: "torch.Tensor",
    eps: "torch.Tensor",
    alpha_bar_t: "torch.Tensor",
    *,
    enabled: bool,
) -> "torch.Tensor":
    """Historical PEERFIX timestep-weighted denoising loss.

    Weighting is part of the predeclared TabDDPM semantics. It is not tuned from
    Gate 0.4 outcomes. When disabled, this reduces exactly to ordinary MSE.
    """
    sq = (pred - eps) ** 2
    if not enabled:
        return torch.mean(sq)
    weights = 1.0 / torch.sqrt(alpha_bar_t + 1e-8)
    return torch.mean(weights.unsqueeze(-1) * sq)


class _Denoiser(nn.Module if nn is not None else object):
    def __init__(self, d: int, timesteps: int, hidden: int, n_layers: int, dropout: float):
        if nn is None:  # pragma: no cover
            raise RuntimeError("PyTorch is required for PEERFIX_small_n_TabDDPM")
        super().__init__()
        self.x_proj = nn.Linear(d, hidden)
        self.t_embed = nn.Embedding(timesteps, hidden)
        blocks: list[nn.Module] = []
        for _ in range(n_layers):
            blocks.extend([
                nn.LayerNorm(hidden),
                nn.Linear(hidden, hidden),
                nn.SiLU(),
                nn.Dropout(dropout),
            ])
        self.blocks = nn.Sequential(*blocks)
        self.out = nn.Linear(hidden, d)

    def forward(self, x: "torch.Tensor", t: "torch.Tensor") -> "torch.Tensor":
        h0 = self.x_proj(x) + self.t_embed(t)
        h = self.blocks(h0)
        return self.out(h + h0)


class SmallNTabDDPM:
    """Numerical small-n DDPM used by the PEERFIX pre-freeze Core.

    This is a clean implementation, not a proxy for another generator. It preserves the
    predeclared/historical PEERFIX TabDDPM semantics relevant to Gate 0.4: robust scaling,
    discrete-aware bootstrap augmentation, timestep-weighted denoising loss, cosine
    diffusion, posterior-variance reverse sampling, gradient clipping, LR scheduling and
    early stopping. No response clipping is performed.
    """

    def __init__(self, config: TabDDPMConfig | None = None, *, device: str | None = None):
        if torch is None:
            raise RuntimeError("PyTorch is required for PEERFIX_small_n_TabDDPM")
        self.config = config or TabDDPMConfig()
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.columns: list[str] = []
        self.robust: RobustScaler | None = None
        self.standard: StandardScaler | None = None
        self.model: _Denoiser | None = None
        self.betas: torch.Tensor | None = None
        self.alphas: torch.Tensor | None = None
        self.alpha_bar: torch.Tensor | None = None
        self.alpha_bar_prev: torch.Tensor | None = None
        self.posterior_variance: torch.Tensor | None = None
        self.discrete_mask: np.ndarray | None = None

    @staticmethod
    def _detect_discrete_mask(df: pd.DataFrame, max_unique: int = DISCRETE_MAX_UNIQUE) -> np.ndarray:
        """Identify DOE-like numeric columns that must not receive bootstrap jitter."""
        mask: list[bool] = []
        for col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                mask.append(False)
                continue
            mask.append(int(df[col].nunique(dropna=True)) <= int(max_unique))
        return np.asarray(mask, dtype=bool)

    def _normalize_fit(self, x: np.ndarray) -> np.ndarray:
        if self.config.robust_normalization:
            self.robust = RobustScaler(quantile_range=(25.0, 75.0)).fit(x)
            xr = self.robust.transform(x)
        else:
            self.robust = None
            xr = x
        self.standard = StandardScaler().fit(xr)
        return self.standard.transform(xr).astype(np.float32)

    def _normalize_inverse(self, z: np.ndarray) -> np.ndarray:
        if self.standard is None:
            raise RuntimeError("TabDDPM scaler not fitted")
        xr = self.standard.inverse_transform(z)
        if self.robust is not None:
            xr = self.robust.inverse_transform(xr)
        # Deliberately no percentile/min-max clipping: Gate 0.4 forbids target clipping.
        return xr

    def _augment(self, z: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        if not self.config.bootstrap_augment or self.config.bootstrap_factor <= 1:
            return z
        n = len(z) * int(self.config.bootstrap_factor)
        idx = rng.choice(len(z), size=n, replace=True)
        out = z[idx].copy()
        if self.config.bootstrap_noise_std > 0:
            noise = rng.normal(0.0, self.config.bootstrap_noise_std, out.shape).astype(np.float32)
            if self.discrete_mask is not None and self.discrete_mask.any():
                noise[:, self.discrete_mask] = 0.0
            out += noise
        return out

    def fit(self, df: pd.DataFrame, *, seed: int) -> "SmallNTabDDPM":
        _seed_all(seed)
        if not all(pd.api.types.is_numeric_dtype(df[c]) for c in df.columns):
            raise TypeError("PEERFIX_small_n_TabDDPM currently requires an all-numeric table")
        self.columns = list(df.columns)
        self.discrete_mask = self._detect_discrete_mask(df)
        x = df.to_numpy(dtype=np.float32, copy=True)
        if not np.isfinite(x).all():
            raise ValueError("TabDDPM input contains non-finite values")
        z = self._normalize_fit(x)
        rng = np.random.default_rng(seed)
        z = self._augment(z, rng)

        cfg = self.config
        d = z.shape[1]
        self.model = _Denoiser(d, cfg.timesteps, cfg.hidden_dim, cfg.n_layers, cfg.dropout).to(self.device)
        betas_np = _cosine_betas(cfg.timesteps)
        self.betas = torch.tensor(betas_np, dtype=torch.float32, device=self.device)
        self.alphas = 1.0 - self.betas
        self.alpha_bar = torch.cumprod(self.alphas, dim=0)
        self.alpha_bar_prev = torch.cat([
            torch.ones(1, dtype=self.alpha_bar.dtype, device=self.device),
            self.alpha_bar[:-1],
        ])
        self.posterior_variance = self.betas * (
            1.0 - self.alpha_bar_prev
        ) / torch.clamp(1.0 - self.alpha_bar, min=1e-12)
        self.posterior_variance = torch.clamp(self.posterior_variance, min=0.0)

        opt = torch.optim.AdamW(
            self.model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay
        )
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            opt, mode="min", factor=cfg.scheduler_factor, patience=cfg.scheduler_patience
        )
        zt = torch.tensor(z, dtype=torch.float32, device=self.device)
        best_loss = float("inf")
        best_state: dict[str, Any] | None = None
        no_improve = 0

        for _epoch in range(cfg.epochs):
            perm = torch.randperm(len(zt), device=self.device)
            losses: list[float] = []
            self.model.train()
            for start in range(0, len(zt), cfg.batch_size):
                xb = zt[perm[start:start + cfg.batch_size]]
                t = torch.randint(0, cfg.timesteps, (len(xb),), device=self.device)
                eps = torch.randn_like(xb)
                abar = self.alpha_bar[t]
                noisy = torch.sqrt(abar).unsqueeze(1) * xb + torch.sqrt(1.0 - abar).unsqueeze(1) * eps
                pred = self.model(noisy, t)
                loss = _weighted_denoising_mse(
                    pred,
                    eps,
                    abar,
                    enabled=cfg.timestep_loss_weighting,
                )
                opt.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), cfg.gradient_clip)
                opt.step()
                losses.append(float(loss.detach().cpu()))
            epoch_loss = float(np.mean(losses))
            scheduler.step(epoch_loss)
            if epoch_loss < best_loss - cfg.min_delta:
                best_loss = epoch_loss
                best_state = {k: v.detach().cpu().clone() for k, v in self.model.state_dict().items()}
                no_improve = 0
            else:
                no_improve += 1
                if no_improve >= cfg.patience:
                    break

        if best_state is not None:
            self.model.load_state_dict(best_state)
        return self

    @torch.no_grad() if torch is not None else (lambda f: f)
    def sample(self, n: int, *, seed: int) -> pd.DataFrame:
        if (
            self.model is None
            or self.betas is None
            or self.alphas is None
            or self.alpha_bar is None
            or self.posterior_variance is None
        ):
            raise RuntimeError("call fit() before sample()")
        _seed_all(seed)
        self.model.eval()
        x = torch.randn((int(n), len(self.columns)), device=self.device)
        for ti in reversed(range(self.config.timesteps)):
            t = torch.full((int(n),), ti, dtype=torch.long, device=self.device)
            eps_hat = self.model(x, t)
            alpha_t = self.alphas[ti]
            abar_t = self.alpha_bar[ti]
            beta_t = self.betas[ti]
            mean = (x - (beta_t / torch.sqrt(1.0 - abar_t)) * eps_hat) / torch.sqrt(alpha_t)
            if ti > 0:
                variance_t = self.posterior_variance[ti]
                x = mean + torch.sqrt(variance_t) * torch.randn_like(x)
            else:
                x = mean
        arr = self._normalize_inverse(x.detach().cpu().numpy())
        return pd.DataFrame(arr, columns=self.columns)
