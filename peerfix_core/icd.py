from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t as student_t

from .seeds import derive_seed


def _reference_levels(real_df: pd.DataFrame, factors: list[str]) -> dict[str, list[float]]:
    levels = {}
    for f in factors:
        vals = sorted(pd.to_numeric(real_df[f], errors="coerce").dropna().unique().tolist())
        if len(vals) not in (2, 3):
            raise ValueError(f"factor {f} must have 2 or 3 declared levels for coded PEERFIX2 ICD")
        levels[f] = vals
    return levels


def _code_series(s: pd.Series, levels: list[float]) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    if len(levels) == 2:
        lo, hi = levels
        return x.map(lambda v: -1.0 if np.isclose(v, lo) else (1.0 if np.isclose(v, hi) else np.nan))
    lo, mid, hi = levels
    def code(v: float) -> float:
        if np.isclose(v, lo): return -1.0
        if np.isclose(v, mid): return 0.0
        if np.isclose(v, hi): return 1.0
        return np.nan
    return x.map(code)


def _design(df: pd.DataFrame, factors: list[str], levels: dict[str, list[float]]) -> pd.DataFrame:
    X = pd.DataFrame(index=df.index)
    for f in factors:
        X[f] = _code_series(df[f], levels[f])
    for a, b in itertools.combinations(factors, 2):
        X[f"{a}:{b}"] = X[a] * X[b]
    return sm.add_constant(X, has_constant="add")


def _fit(df: pd.DataFrame, target: str, factors: list[str], levels: dict[str, list[float]]):
    X = _design(df, factors, levels)
    y = pd.to_numeric(df[target], errors="coerce")
    ok = X.notna().all(axis=1) & y.notna()
    if ok.sum() <= X.shape[1]:
        raise ValueError("insufficient complete rows to fit factorial model")
    return sm.OLS(y.loc[ok].astype(float), X.loc[ok].astype(float)).fit()


def evaluate_icd_matched_n(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    *,
    target: str,
    factors: list[str],
    reference_terms: list[str],
    matched_n: int | None = None,
    n_subsamples: int = 1000,
    alpha: float = 0.05,
    lam: float = 0.10,
    master_seed: int = 123,
    scenario: str = "baseline_0pct",
    generator: str = "generator",
    realisation: int = 1,
) -> dict[str, object]:
    """Candidate PEERFIX-Core ICD with matched-effective-n stability components."""
    levels = _reference_levels(real_df, factors)
    real_model = _fit(real_df, target, factors, levels)
    n_match = int(matched_n or len(real_df))
    if len(synthetic_df) < n_match:
        raise ValueError("synthetic_df smaller than matched_n; without-replacement sampling required")

    candidate_terms = [t for t in real_model.params.index if t != "const"]
    unknown_terms = [t for t in candidate_terms if t not in reference_terms]

    real_info = {}
    for term in reference_terms:
        if term not in real_model.params.index:
            raise KeyError(f"reference term not in model: {term}")
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

    acc = {term: {"S": [], "M": [], "D": [], "beta": [], "p": []} for term in reference_terms}
    spurious_rates: list[float] = []
    seed = derive_seed(
        master_seed,
        purpose="icd_matched_n",
        scenario=scenario,
        generator=generator,
        realisation=realisation,
    )
    rng = np.random.default_rng(seed)
    for _ in range(n_subsamples):
        idx = rng.choice(len(synthetic_df), size=n_match, replace=False)
        sub = synthetic_df.iloc[idx].reset_index(drop=True)
        model = _fit(sub, target, factors, levels)
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
            if p_syn < alpha and p_real >= alpha:
                spur += 1
        spurious_rates.append(spur / len(unknown_terms) if unknown_terms else 0.0)

    effect_rows = []
    for term in reference_terms:
        effect_rows.append({
            "term": term,
            **real_info[term],
            "S": float(np.mean(acc[term]["S"])),
            "M": float(np.mean(acc[term]["M"])),
            "D": float(np.mean(acc[term]["D"])),
            "beta_synth_median": float(np.median(acc[term]["beta"])),
            "p_synth_median": float(np.median(acc[term]["p"])),
        })
    effects = pd.DataFrame(effect_rows)
    mean_S = float(effects["S"].mean())
    mean_M = float(effects["M"].mean())
    mean_D = float(effects["D"].mean())
    R = float(np.mean(spurious_rates))
    icd = float(np.mean([mean_S, mean_M, mean_D]) - lam * R)
    return {
        "ICD": icd,
        "mean_S": mean_S,
        "mean_M": mean_M,
        "mean_D": mean_D,
        "spurious_rate": R,
        "matched_n": n_match,
        "n_subsamples": n_subsamples,
        "seed": seed,
        "effects": effects,
    }


def _legacy_strength(beta: float) -> tuple[str, float]:
    a = abs(float(beta))
    if a < 0.30:
        return "weak", 0.5
    if a < 0.60:
        return "moderate", 0.3
    return "strong", 0.2


def evaluate_icd_legacy_full_n(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    *,
    target: str,
    factors: list[str],
    reference_terms: list[str],
    alpha: float = 0.05,
    lam: float = 0.10,
) -> dict[str, object]:
    """Historical PEERFIX ICD on the full synthetic realization.

    This is retained ONLY for historical comparability. Its detectability component uses
    p-values from the full synthetic sample and therefore must not be interpreted as added
    biological evidence. Primary PEERFIX-Core inference uses ``evaluate_icd_matched_n``.
    """
    levels = _reference_levels(real_df, factors)
    real_model = _fit(real_df, target, factors, levels)
    synth_model = _fit(synthetic_df, target, factors, levels)
    candidate_terms = [t for t in real_model.params.index if t != "const"]
    unknown_terms = [t for t in candidate_terms if t not in reference_terms]

    effects_rows: list[dict[str, object]] = []
    for term in reference_terms:
        if term not in real_model.params.index:
            raise KeyError(f"reference term not in model: {term}")
        beta_real = float(real_model.params[term])
        p_real = float(real_model.pvalues[term])
        beta_syn = float(synth_model.params.get(term, np.nan))
        p_syn = float(synth_model.pvalues.get(term, np.nan))
        strength, tol = _legacy_strength(beta_real)
        S = float(np.isfinite(beta_syn) and np.sign(beta_syn) == np.sign(beta_real))
        M = float(np.isfinite(beta_syn) and abs(beta_real - beta_syn) <= tol)
        D = float(np.isfinite(p_syn) and p_syn < alpha)
        effects_rows.append({
            "term": term,
            "beta_real": beta_real,
            "p_real": p_real,
            "beta_synth": beta_syn,
            "p_synth": p_syn,
            "strength": strength,
            "magnitude_tolerance": tol,
            "S": S,
            "M": M,
            "D": D,
        })

    effects = pd.DataFrame(effects_rows)
    spurious = 0
    for term in unknown_terms:
        p_real = float(real_model.pvalues.get(term, 1.0))
        p_syn = float(synth_model.pvalues.get(term, 1.0))
        if np.isfinite(p_syn) and p_syn < alpha and p_real >= alpha:
            spurious += 1
    R = float(spurious / len(unknown_terms)) if unknown_terms else 0.0
    mean_S = float(effects["S"].mean())
    mean_M = float(effects["M"].mean())
    mean_D = float(effects["D"].mean())
    return {
        "ICD": float(np.mean([mean_S, mean_M, mean_D]) - lam * R),
        "mean_S": mean_S,
        "mean_M": mean_M,
        "mean_D": mean_D,
        "spurious_rate": R,
        "n_synthetic": int(len(synthetic_df)),
        "effects": effects,
        "historical_comparability_only": True,
    }
