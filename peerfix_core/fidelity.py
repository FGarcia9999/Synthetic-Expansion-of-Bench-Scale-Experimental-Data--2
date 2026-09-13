from __future__ import annotations

import itertools
from typing import Mapping

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, pearsonr, wasserstein_distance


def _numeric(series: pd.Series, name: str) -> np.ndarray:
    x = pd.to_numeric(series, errors="coerce").to_numpy(float)
    if not np.isfinite(x).all():
        raise ValueError(f"non-finite values in {name}")
    return x


def continuous_univariate_fidelity(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for col in columns:
        if col not in real_df.columns or col not in synthetic_df.columns:
            raise KeyError(col)
        xr = _numeric(real_df[col], f"real:{col}")
        xs = _numeric(synthetic_df[col], f"synthetic:{col}")
        ks = ks_2samp(xr, xs, alternative="two-sided", mode="auto")
        rows.append(
            {
                "column": col,
                "ks_statistic": float(ks.statistic),
                "wasserstein_distance": float(wasserstein_distance(xr, xs)),
            }
        )
    return pd.DataFrame(rows)


def designed_support_fidelity(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    support: Mapping[str, list[float]],
) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for col, declared_levels in support.items():
        if col not in real_df.columns or col not in synthetic_df.columns:
            raise KeyError(col)
        levels = np.asarray(declared_levels, dtype=float)
        xr = _numeric(real_df[col], f"real:{col}")
        xs = _numeric(synthetic_df[col], f"synthetic:{col}")

        def on_level(v: float) -> bool:
            return bool(np.any(np.isclose(v, levels)))

        off_support = float(np.mean([not on_level(v) for v in xs])) if len(xs) else float("nan")
        present = sum(bool(np.any(np.isclose(xs[:, None], lv))) for lv in levels)
        coverage = float(present / len(levels)) if len(levels) else float("nan")

        pr = np.asarray([np.mean(np.isclose(xr, lv)) for lv in levels], dtype=float)
        ps = np.asarray([np.mean(np.isclose(xs, lv)) for lv in levels], dtype=float)
        tvd = float(0.5 * np.abs(pr - ps).sum())
        rows.append(
            {
                "column": col,
                "support_coverage": coverage,
                "total_variation_distance": tvd,
                "off_support_fraction": off_support,
            }
        )
    return pd.DataFrame(rows)


def correlation_fidelity(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    columns: list[str],
) -> dict[str, float]:
    if len(columns) < 2:
        raise ValueError("at least two columns are required")
    rr = real_df[columns].apply(pd.to_numeric, errors="coerce")
    ss = synthetic_df[columns].apply(pd.to_numeric, errors="coerce")
    if rr.isna().any().any() or ss.isna().any().any():
        raise ValueError("non-numeric/missing values in correlation fidelity input")
    rc = rr.corr().to_numpy(float)
    sc = ss.corr().to_numpy(float)
    iu = np.triu_indices(len(columns), k=1)
    rv = rc[iu]
    sv = sc[iu]
    finite = np.isfinite(rv) & np.isfinite(sv)
    if finite.sum() >= 2 and np.std(rv[finite]) > 0 and np.std(sv[finite]) > 0:
        corr_of_corr = float(pearsonr(rv[finite], sv[finite]).statistic)
    else:
        corr_of_corr = float("nan")
    diff = rc - sc
    return {
        "correlation_of_correlations": corr_of_corr,
        "frobenius_norm_correlation_difference": float(np.linalg.norm(diff, ord="fro")),
    }


def doe_structure_fidelity(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    factors: list[str],
) -> dict[str, float]:
    """Evaluate experimental-cell and marginal factor-frequency preservation.

    The real set defines the authorized DOE cells. Synthetic combinations outside those
    cells are retained (not silently filtered) and reported through ``off_design_cell_fraction``.
    """
    for col in factors:
        if col not in real_df.columns or col not in synthetic_df.columns:
            raise KeyError(col)

    real_tuples = [tuple(row) for row in real_df[factors].to_numpy()]
    synth_tuples = [tuple(row) for row in synthetic_df[factors].to_numpy()]
    real_cells = set(real_tuples)
    synth_cells = set(synth_tuples)
    coverage = float(len(real_cells & synth_cells) / len(real_cells)) if real_cells else float("nan")
    off_design = float(np.mean([t not in real_cells for t in synth_tuples])) if synth_tuples else float("nan")

    marginal_abs_diffs: list[float] = []
    for factor in factors:
        levels = sorted(pd.to_numeric(real_df[factor], errors="coerce").dropna().unique().tolist())
        xr = _numeric(real_df[factor], f"real:{factor}")
        xs = _numeric(synthetic_df[factor], f"synthetic:{factor}")
        for lv in levels:
            marginal_abs_diffs.append(abs(float(np.mean(np.isclose(xr, lv))) - float(np.mean(np.isclose(xs, lv)))))

    return {
        "factorial_cell_coverage": coverage,
        "off_design_cell_fraction": off_design,
        "factor_level_frequency_deviation": float(np.mean(marginal_abs_diffs)) if marginal_abs_diffs else float("nan"),
    }


def evaluate_fidelity_bundle(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    *,
    factors: list[str],
    target: str,
    support: Mapping[str, list[float]],
) -> dict[str, object]:
    """Protocol-aligned fidelity bundle for one synthetic realisation."""
    return {
        "continuous": continuous_univariate_fidelity(real_df, synthetic_df, [target]),
        "support": designed_support_fidelity(real_df, synthetic_df, support),
        "correlation": correlation_fidelity(real_df, synthetic_df, factors + [target]),
        "doe": doe_structure_fidelity(real_df, synthetic_df, factors),
    }
