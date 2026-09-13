from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


def compute_dcr(
    real_reference: pd.DataFrame,
    synthetic: pd.DataFrame,
    feature_cols: list[str],
) -> np.ndarray:
    """DCR diagnostic only, standardized on the real reference set."""
    if not feature_cols:
        raise ValueError("feature_cols cannot be empty")
    Xr = real_reference[feature_cols].apply(pd.to_numeric, errors="coerce")
    Xs = synthetic[feature_cols].apply(pd.to_numeric, errors="coerce")
    med = Xr.median(numeric_only=True)
    Xr = Xr.fillna(med)
    Xs = Xs.fillna(med)
    scaler = StandardScaler().fit(Xr)
    Xr_s = scaler.transform(Xr)
    Xs_s = scaler.transform(Xs)
    nn = NearestNeighbors(n_neighbors=1).fit(Xr_s)
    d, _ = nn.kneighbors(Xs_s)
    return d[:, 0]


def summarize_dcr(values: np.ndarray, threshold: float = 0.10) -> dict[str, float]:
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return {k: float("nan") for k in ["min", "p05", "median", "p95", "fraction_below_0p10"]}
    return {
        "min": float(np.min(v)),
        "p05": float(np.quantile(v, 0.05)),
        "median": float(np.median(v)),
        "p95": float(np.quantile(v, 0.95)),
        "fraction_below_0p10": float(np.mean(v < threshold)),
    }
