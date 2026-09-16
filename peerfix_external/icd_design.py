from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t as student_t

from peerfix_core.seeds import derive_seed


def build_design_matrix(
    df: pd.DataFrame,
    *,
    factors: list[str],
    include_two_way: bool = True,
    include_quadratic: bool = False,
) -> pd.DataFrame:
    """Build an adapter-declared coded DOE design matrix.

    The external workbook already provides the authoritative coded coordinates.
    This function changes only the design representation; the frozen ICD components
    (S/M/D, matched effective n, spurious penalty and lambda) remain unchanged.
    """
    X = pd.DataFrame(index=df.index)
    for factor in factors:
        if factor not in df.columns:
            raise KeyError(factor)
        X[factor] = pd.to_numeric(df[factor], errors="coerce").astype(float)

    if include_two_way:
        for i, a in enumerate(factors):
            for b in factors[i + 1 :]:
                X[f"{a}:{b}"] = X[a] * X[b]

    if include_quadratic:
        for factor in factors:
            X[f"{factor}^2"] = X[factor] ** 2

    return sm.add_constant(X, has_constant="add")


def fit_design_model(
    df: pd.DataFrame,
    *,
    target: str,
    factors: list[str],
    include_two_way: bool = True,
    include_quadratic: bool = False,
):
    X = build_design_matrix(
        df,
        factors=factors,
        include_two_way=include_two_way,
        include_quadratic=include_quadratic,
    )
    if target not in df.columns:
        raise KeyError(target)
    y = pd.to_numeric(df[target], errors="coerce")
    ok = X.notna().all(axis=1) & y.notna()
    if int(ok.sum()) <= X.shape[1]:
        raise ValueError(
            f"insufficient complete rows for external DOE model: {int(ok.sum())} rows, "
            f"{X.shape[1]} parameters"
        )
    return sm.OLS(y.loc[ok].astype(float), X.loc[ok].astype(float)).fit()


def evaluate_design_icd_matched_n(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    *,
    target: str,
    factors: list[str],
    reference_terms: Iterable[str],
    include_two_way: bool = True,
    include_quadratic: bool = False,
    matched_n: int | None = None,
    n_subsamples: int = 1000,
    alpha: float = 0.05,
    lam: float = 0.10,
    master_seed: int = 123,
    scenario: str = "baseline_0pct",
    generator: str = "generator",
    realisation: int = 1,
) -> dict[str, object]:
    """Frozen PEERFIX matched-n ICD applied to an adapter-defined DOE model.

    Only the design matrix is adapter-specific. The scientific concordance logic is
    identical to PEERFIX-Core v1.0: sign preservation (S), real-uncertainty-band
    magnitude preservation (M), detectability (D), matched-n spurious-rate penalty
    and ``ICD = mean(S, M, D) - lambda * R``.
    """
    reference_terms = list(reference_terms)
    if not reference_terms:
        raise ValueError("reference_terms must be non-empty for positive-domain ICD")

    real_model = fit_design_model(
        real_df,
        target=target,
        factors=factors,
        include_two_way=include_two_way,
        include_quadratic=include_quadratic,
    )
    n_match = int(matched_n or len(real_df))
    if len(synthetic_df) < n_match:
        raise ValueError("synthetic_df smaller than matched_n; sampling is without replacement")

    candidate_terms = [t for t in real_model.params.index if t != "const"]
    unknown_terms = [t for t in candidate_terms if t not in reference_terms]

    real_info: dict[str, dict[str, float]] = {}
    for term in reference_terms:
        if term not in real_model.params.index:
            raise KeyError(f"reference term not in adapter design model: {term}")
        beta = float(real_model.params[term])
        se = float(real_model.bse[term])
        df_resid = float(real_model.df_resid)
        crit = float(student_t.ppf(0.975, df_resid))
        real_info[term] = {
            "beta_real": beta,
            "se_real": se,
            "band_low": beta - crit * se,
            "band_high": beta + crit * se,
            "p_real": float(real_model.pvalues[term]),
        }

    acc = {
        term: {"S": [], "M": [], "D": [], "beta": [], "p": []}
        for term in reference_terms
    }
    spurious_rates: list[float] = []
    seed = derive_seed(
        master_seed,
        purpose="icd_matched_n",
        scenario=scenario,
        generator=generator,
        realisation=realisation,
    )
    rng = np.random.default_rng(seed)

    for _ in range(int(n_subsamples)):
        idx = rng.choice(len(synthetic_df), size=n_match, replace=False)
        sub = synthetic_df.iloc[idx].reset_index(drop=True)
        model = fit_design_model(
            sub,
            target=target,
            factors=factors,
            include_two_way=include_two_way,
            include_quadratic=include_quadratic,
        )
        for term in reference_terms:
            info = real_info[term]
            beta = float(model.params.get(term, np.nan))
            p = float(model.pvalues.get(term, np.nan))
            acc[term]["beta"].append(beta)
            acc[term]["p"].append(p)
            acc[term]["S"].append(float(np.sign(beta) == np.sign(info["beta_real"])))
            acc[term]["M"].append(float(info["band_low"] <= beta <= info["band_high"]))
            acc[term]["D"].append(float(p < alpha))

        spur = 0
        for term in unknown_terms:
            p_real = float(real_model.pvalues.get(term, 1.0))
            p_syn = float(model.pvalues.get(term, 1.0))
            if np.isfinite(p_syn) and p_syn < alpha and p_real >= alpha:
                spur += 1
        spurious_rates.append(spur / len(unknown_terms) if unknown_terms else 0.0)

    effect_rows: list[dict[str, float | str]] = []
    for term in reference_terms:
        effect_rows.append(
            {
                "term": term,
                **real_info[term],
                "S": float(np.mean(acc[term]["S"])),
                "M": float(np.mean(acc[term]["M"])),
                "D": float(np.mean(acc[term]["D"])),
                "beta_synth_median": float(np.median(acc[term]["beta"])),
                "p_synth_median": float(np.median(acc[term]["p"])),
            }
        )

    effects = pd.DataFrame(effect_rows)
    mean_S = float(effects["S"].mean())
    mean_M = float(effects["M"].mean())
    mean_D = float(effects["D"].mean())
    R = float(np.mean(spurious_rates))
    return {
        "ICD": float(np.mean([mean_S, mean_M, mean_D]) - lam * R),
        "mean_S": mean_S,
        "mean_M": mean_M,
        "mean_D": mean_D,
        "spurious_rate": R,
        "matched_n": n_match,
        "n_subsamples": int(n_subsamples),
        "seed": int(seed),
        "effects": effects,
        "adapter_design": {
            "include_two_way": bool(include_two_way),
            "include_quadratic": bool(include_quadratic),
        },
    }
