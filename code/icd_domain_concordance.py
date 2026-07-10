"""
icd_domain_concordance.py
==========================

Indice de Concordancia com Conhecimento de Dominio (ICD)
-----------------------------------------------------------
Metrica complementar ao protocolo fidelidade-utilidade-risco (KS/Wasserstein,
corr_of_corr, TSTR/TRTR, DCR) ja usado no pipeline de expansao sintetica de
dados de bancada sobre producao de biossurfactante por Candida lipolytica.

Motivacao
---------
Metricas de fidelidade generica (KS, Wasserstein, corr_of_corr) respondem a
pergunta "o dado sintetico se parece estatisticamente com o dado real?".
Elas NAO respondem a pergunta cientificamente mais relevante para um estudo
de bancada com desenho fatorial: "o dado sintetico preserva os efeitos
principais e as interacoes que o experimento original ja demonstrou serem
reais (Pareto/ANOVA, p<0.05)?".

O ICD ancora a validacao em conhecimento de dominio *externo* (os efeitos
ja validados estatisticamente no experimento fatorial original), em vez de
depender apenas de autoconsistencia estatistica interna entre real e
sintetico. Ele opera sobre os COEFICIENTES de um modelo fatorial codificado
(-1/0/+1), o mesmo tipo de modelo por tras de uma analise de Pareto de
efeitos, e nao sobre a matriz de correlacao bruta -- que mistura efeitos
principais, interacoes e ruido sem separa-los.

Tres criterios por efeito conhecido, todos binarios (0/1) para permanecerem
auditaveis por um revisor sem depender de testes estatisticos sofisticados:

    S (Sign)         -> o sinal do coeficiente sintetico bate com o sinal
                         do coeficiente real?
    M (Magnitude)     -> o coeficiente sintetico cai dentro de uma banda de
                         tolerancia adaptativa a forca do efeito real (efeitos
                         fracos toleram desvio absoluto maior que efeitos
                         fortes, refletindo que a distribuicao amostral do
                         coeficiente e mais estreita quanto maior o efeito
                         verdadeiro)?
    D (Detectavel)    -> o efeito ainda e estatisticamente significativo
                         (p < alpha) no modelo ajustado aos dados sinteticos?

Um termo de penalidade (P) contabiliza efeitos ESPURIOS: termos que NAO
faziam parte da lista de efeitos conhecidos e que se tornam "significativos"
apenas nos dados sinteticos -- sinal de que o gerador esta inventando
estrutura que o experimento real nao sustenta.

    ICD_g = mean(S, M, D)  -  lambda * taxa_de_termos_espurios

Uso tipico
----------
    known_effects = [
        KnownEffect("seawater_vv:urea_pv",         "Agua do mar x ureia (interacao negativa)"),
        KnownEffect("urea_pv:kh2po4_pv",           "Ureia x KH2PO4 (interacao positiva)"),
        KnownEffect("ammonium_sulfate_pv:kh2po4_pv","Sulfato de amonio x KH2PO4 (sinergia positiva)"),
        KnownEffect("seawater_vv",                  "Agua do mar (efeito principal negativo)"),
    ]

    summary, per_effect_tables = evaluate_generators(
        real_df=real_df,
        synth_dfs={"gaussian_copula": df_gc, "ctgan": df_ct, "tvae": df_tv, "tabddpm": df_td},
        factors=["seawater_vv", "urea_pv", "ammonium_sulfate_pv", "kh2po4_pv"],
        interactions=[("seawater_vv","urea_pv"), ("urea_pv","kh2po4_pv"),
                      ("ammonium_sulfate_pv","kh2po4_pv")],
        target="surface_tension_mNm",
        known_effects=known_effects,
    )

Requisitos: pandas, numpy, statsmodels
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple, Literal

import numpy as np
import pandas as pd
import statsmodels.api as sm

StrengthCategory = Literal["weak", "moderate", "strong"]

# Bandas de tolerancia adaptativas (desvio absoluto maximo tolerado entre
# coeficiente real e sintetico, em unidades do proprio coeficiente).
TOLERANCE_BANDS: Dict[StrengthCategory, float] = {
    "weak": 0.5,
    "moderate": 0.3,
    "strong": 0.2,
}

# Cortes usados para classificar a forca de um efeito a partir do
# coeficiente padronizado (-1/0/+1 coding), analogos aos usados na
# literatura para |r| de Pearson.
WEAK_CUT = 0.30
STRONG_CUT = 0.60


# --------------------------------------------------------------------------- #
# Estruturas de dados
# --------------------------------------------------------------------------- #

@dataclass
class KnownEffect:
    """Um efeito (principal ou de interacao) ja validado no experimento real.

    term: precisa bater exatamente com o nome de coluna produzido por
          build_design_matrix (ex.: "seawater_vv" para efeito principal,
          "seawater_vv:urea_pv" para interacao).
    label: descricao legivel usada nas tabelas de saida.
    """
    term: str
    label: str


@dataclass
class EffectResult:
    term: str
    label: str
    coef_real: float
    p_real: float
    coef_synth: float
    p_synth: float
    category: Optional[StrengthCategory]
    S: Optional[int]
    M: Optional[int]
    D: Optional[int]


@dataclass
class GeneratorICD:
    generator: str
    icd: float
    mean_S: float
    mean_M: float
    mean_D: float
    spurious_rate: float
    n_known_effects: int
    n_unknown_terms: int
    effects: pd.DataFrame  # tabela detalhada por efeito (para auditoria)


# --------------------------------------------------------------------------- #
# Codificacao do desenho fatorial (-1 / 0 / +1)
# --------------------------------------------------------------------------- #

def get_reference_levels(real_df: pd.DataFrame, factors: Sequence[str]) -> Dict[str, List[float]]:
    """Extrai os niveis (ordenados) de cada fator a partir do dataset REAL.

    Os dados sinteticos sao codificados usando esses mesmos niveis de
    referencia (nunca os niveis "aparentes" do proprio dataset sintetico),
    para que -1/0/+1 signifique exatamente a mesma coisa nos dois lados da
    comparacao.
    """
    return {f: sorted(real_df[f].unique().tolist()) for f in factors}


def _snap_and_code(value: float, levels: Sequence[float]) -> float:
    """Mapeia um valor continuo para o nivel de referencia mais proximo e
    devolve o codigo -1/0/+1 (ou z-score se o fator nao tiver 3 niveis)."""
    if len(levels) == 3:
        lo, mid, hi = levels
        dists = [abs(value - lo), abs(value - mid), abs(value - hi)]
        idx = int(np.argmin(dists))
        return [-1.0, 0.0, 1.0][idx]
    # fallback generico para fatores com != 3 niveis: padronizacao simples
    arr = np.asarray(levels, dtype=float)
    mu, sd = arr.mean(), arr.std(ddof=0)
    return (value - mu) / sd if sd > 0 else 0.0


def code_with_reference(
    df: pd.DataFrame, factors: Sequence[str], reference_levels: Dict[str, List[float]]
) -> pd.DataFrame:
    """Aplica a codificacao -1/0/+1 a um dataframe (real ou sintetico),
    usando SEMPRE os niveis de referencia do dataset real."""
    coded = df.copy()
    for f in factors:
        levels = reference_levels[f]
        coded[f] = df[f].apply(lambda v, lv=levels: _snap_and_code(v, lv))
    return coded


def build_design_matrix(
    coded_df: pd.DataFrame, factors: Sequence[str], interactions: Sequence[Tuple[str, str]] = ()
) -> pd.DataFrame:
    """Monta a matriz de projeto (main effects + interacoes de 2 vias) a
    partir de um dataframe ja codificado em -1/0/+1."""
    X = coded_df[list(factors)].copy()
    for a, b in interactions:
        X[f"{a}:{b}"] = coded_df[a] * coded_df[b]
    X = sm.add_constant(X, has_constant="add")
    return X


def classify_strength(coef: float, weak_cut: float = WEAK_CUT, strong_cut: float = STRONG_CUT) -> StrengthCategory:
    a = abs(coef)
    if a < weak_cut:
        return "weak"
    elif a < strong_cut:
        return "moderate"
    return "strong"


# --------------------------------------------------------------------------- #
# Ajuste do modelo fatorial
# --------------------------------------------------------------------------- #

def fit_factorial_model(
    df: pd.DataFrame,
    factors: Sequence[str],
    interactions: Sequence[Tuple[str, str]],
    target: str,
    reference_levels: Dict[str, List[float]],
) -> sm.regression.linear_model.RegressionResultsWrapper:
    """Codifica o dataframe e ajusta y ~ fatores + interacoes por OLS."""
    coded = code_with_reference(df, factors, reference_levels)
    X = build_design_matrix(coded, factors, interactions)
    y = df[target].astype(float)
    model = sm.OLS(y, X, missing="drop").fit()
    return model


# --------------------------------------------------------------------------- #
# Criterios S / M / D e penalidade por termos espurios
# --------------------------------------------------------------------------- #

def _sign_match(coef_real: float, coef_synth: float) -> Optional[int]:
    if coef_real == 0 or np.isnan(coef_synth):
        return None
    return int(np.sign(coef_real) == np.sign(coef_synth))


def _magnitude_match(coef_real: float, coef_synth: float, category: StrengthCategory) -> Optional[int]:
    if np.isnan(coef_synth):
        return None
    tol = TOLERANCE_BANDS[category]
    return int(abs(coef_real - coef_synth) <= tol)


def _detectable(p_synth: float, alpha: float) -> Optional[int]:
    if np.isnan(p_synth):
        return None
    return int(p_synth < alpha)


def spurious_term_rate(
    real_model, synth_model, known_terms: Sequence[str], alpha: float = 0.05
) -> Tuple[float, int]:
    """Fracao de termos NAO listados como efeitos conhecidos que aparecem
    como significativos no modelo sintetico sem serem significativos no
    modelo real (estrutura inventada pelo gerador)."""
    all_terms = [t for t in real_model.params.index if t != "const"]
    unknown_terms = [t for t in all_terms if t not in known_terms]
    if not unknown_terms:
        return 0.0, 0
    spurious = 0
    for t in unknown_terms:
        p_real = real_model.pvalues.get(t, 1.0)
        p_synth = synth_model.pvalues.get(t, 1.0)
        if p_synth < alpha and p_real >= alpha:
            spurious += 1
    return spurious / len(unknown_terms), len(unknown_terms)


# --------------------------------------------------------------------------- #
# API principal
# --------------------------------------------------------------------------- #

def compute_icd(
    real_model,
    synth_model,
    known_effects: Sequence[KnownEffect],
    alpha: float = 0.05,
    lam: float = 0.10,
    generator_name: str = "generator",
) -> GeneratorICD:
    rows = []
    for eff in known_effects:
        coef_real = real_model.params.get(eff.term, np.nan)
        p_real = real_model.pvalues.get(eff.term, np.nan)
        coef_synth = synth_model.params.get(eff.term, np.nan)
        p_synth = synth_model.pvalues.get(eff.term, np.nan)

        if np.isnan(coef_real):
            raise KeyError(
                f"Termo '{eff.term}' nao encontrado no modelo real. "
                f"Termos disponiveis: {list(real_model.params.index)}"
            )

        category = classify_strength(coef_real)
        S = _sign_match(coef_real, coef_synth)
        M = _magnitude_match(coef_real, coef_synth, category)
        D = _detectable(p_synth, alpha)

        rows.append(
            EffectResult(
                term=eff.term, label=eff.label,
                coef_real=coef_real, p_real=p_real,
                coef_synth=coef_synth, p_synth=p_synth,
                category=category, S=S, M=M, D=D,
            )
        )

    df_effects = pd.DataFrame([r.__dict__ for r in rows])

    mean_S = df_effects["S"].mean(skipna=True)
    mean_M = df_effects["M"].mean(skipna=True)
    mean_D = df_effects["D"].mean(skipna=True)
    base_score = float(np.nanmean([mean_S, mean_M, mean_D]))

    known_terms = [e.term for e in known_effects]
    spurious_rate, n_unknown = spurious_term_rate(real_model, synth_model, known_terms, alpha=alpha)

    icd = base_score - lam * spurious_rate

    return GeneratorICD(
        generator=generator_name,
        icd=icd,
        mean_S=mean_S, mean_M=mean_M, mean_D=mean_D,
        spurious_rate=spurious_rate,
        n_known_effects=len(known_effects),
        n_unknown_terms=n_unknown,
        effects=df_effects,
    )


def evaluate_generators(
    real_df: pd.DataFrame,
    synth_dfs: Dict[str, pd.DataFrame],
    factors: Sequence[str],
    interactions: Sequence[Tuple[str, str]],
    target: str,
    known_effects: Sequence[KnownEffect],
    alpha: float = 0.05,
    lam: float = 0.10,
) -> Tuple[pd.DataFrame, Dict[str, GeneratorICD]]:
    """Roda o ICD para varios geradores de uma vez.

    Retorna:
        summary_df : uma linha por gerador, com ICD e seus componentes.
        details    : dict gerador -> GeneratorICD (inclui a tabela de
                     efeitos individual, para auditoria linha a linha).
    """
    reference_levels = get_reference_levels(real_df, factors)
    real_model = fit_factorial_model(real_df, factors, interactions, target, reference_levels)

    details: Dict[str, GeneratorICD] = {}
    summary_rows = []
    for name, sdf in synth_dfs.items():
        synth_model = fit_factorial_model(sdf, factors, interactions, target, reference_levels)
        result = compute_icd(real_model, synth_model, known_effects, alpha=alpha, lam=lam, generator_name=name)
        details[name] = result
        summary_rows.append(
            dict(
                generator=name,
                ICD=round(result.icd, 3),
                mean_S=round(result.mean_S, 3),
                mean_M=round(result.mean_M, 3),
                mean_D=round(result.mean_D, 3),
                spurious_rate=round(result.spurious_rate, 3),
            )
        )

    summary_df = pd.DataFrame(summary_rows).sort_values("ICD", ascending=False).reset_index(drop=True)
    return summary_df, details


def checklist_table(details: Dict[str, GeneratorICD]) -> pd.DataFrame:
    """Monta a tabela no formato Sinal/Magnitude/Detectavel (check/X) usada
    no manuscrito, uma linha por efeito conhecido, uma coluna-tripla por
    gerador -- pronta para exportar a uma tabela do artigo."""
    symbol = {1: "v", 0: "x", None: "-"}  # 'v' e usado no lugar de check-mark para evitar problemas de encoding
    first = next(iter(details.values()))
    rows = []
    for _, eff_row in first.effects.iterrows():
        row = {"efeito": eff_row["label"], "sinal_real": "+" if eff_row["coef_real"] > 0 else "-"}
        for gen_name, gen_result in details.items():
            match = gen_result.effects[gen_result.effects["term"] == eff_row["term"]].iloc[0]
            row[f"{gen_name}"] = (
                f"S:{symbol.get(match['S'])} "
                f"M:{symbol.get(match['M'])} "
                f"D:{symbol.get(match['D'])}"
            )
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Demonstracao com dados ILUSTRATIVOS (nao sao os dados reais do estudo)
# --------------------------------------------------------------------------- #

def _build_illustrative_demo():
    """Gera um dataset fatorial ilustrativo (mesma estrutura de colunas do
    estudo: seawater_vv, urea_pv, ammonium_sulfate_pv, kh2po4_pv,
    surface_tension_mNm) e quatro versoes 'sinteticas' com graus de
    preservacao de efeito diferentes, apenas para validar a logica do ICD.
    NAO usa os dados reais do estudo -- e apenas um teste de sanidade.
    """
    rng = np.random.default_rng(42)

    levels = {
        "seawater_vv": [0.0, 50.0, 100.0],
        "urea_pv": [0.0, 0.25, 0.5],
        "ammonium_sulfate_pv": [0.2, 0.4, 0.6],
        "kh2po4_pv": [0.5, 1.0, 1.5],
    }
    factors = list(levels.keys())
    combos = list(itertools.product(*levels.values()))
    rng.shuffle(combos)
    combos = combos[:20]
    real_df = pd.DataFrame(combos, columns=factors)

    def code(v, lv):
        lo, mid, hi = lv
        return {lo: -1.0, mid: 0.0, hi: 1.0}[v]

    coded = pd.DataFrame({f: real_df[f].apply(lambda v, lv=levels[f]: code(v, lv)) for f in factors})

    # Efeitos "verdadeiros" definidos para o teste de sanidade, na mesma
    # direcao qualitativa relatada na dissertacao original:
    true_effects = {
        "seawater_vv": -1.2,                         # efeito principal negativo (forte)
        "urea_pv": 0.1,
        "ammonium_sulfate_pv": 0.9,                  # positivo (moderado/forte)
        "kh2po4_pv": 0.8,                            # positivo (moderado)
        "seawater_vv:urea_pv": -0.9,                 # interacao negativa
        "urea_pv:kh2po4_pv": 0.7,                    # interacao positiva
        "ammonium_sulfate_pv:kh2po4_pv": 0.85,       # sinergia positiva
    }
    y = 48.0
    y = y + true_effects["seawater_vv"] * coded["seawater_vv"]
    y = y + true_effects["urea_pv"] * coded["urea_pv"]
    y = y + true_effects["ammonium_sulfate_pv"] * coded["ammonium_sulfate_pv"]
    y = y + true_effects["kh2po4_pv"] * coded["kh2po4_pv"]
    y = y + true_effects["seawater_vv:urea_pv"] * coded["seawater_vv"] * coded["urea_pv"]
    y = y + true_effects["urea_pv:kh2po4_pv"] * coded["urea_pv"] * coded["kh2po4_pv"]
    y = y + true_effects["ammonium_sulfate_pv:kh2po4_pv"] * coded["ammonium_sulfate_pv"] * coded["kh2po4_pv"]
    y = y + rng.normal(0, 0.3, size=len(y))
    real_df["surface_tension_mNm"] = y

    def make_synth(fidelity: float, spurious_noise: float, seed: int) -> pd.DataFrame:
        """fidelity=1 reproduz bem os efeitos reais; fidelity baixo os degrada."""
        r = np.random.default_rng(seed)
        sdf = real_df[factors].sample(n=20, replace=True, random_state=seed).reset_index(drop=True)
        coded_s = pd.DataFrame({f: sdf[f].apply(lambda v, lv=levels[f]: code(v, lv)) for f in factors})
        ys = 48.0
        for term, val in true_effects.items():
            degraded = val * fidelity + r.normal(0, (1 - fidelity) * 1.0)
            if ":" in term:
                a, b = term.split(":")
                ys = ys + degraded * coded_s[a] * coded_s[b]
            else:
                ys = ys + degraded * coded_s[term]
        ys = ys + r.normal(0, 0.3 + spurious_noise, size=len(ys))
        sdf["surface_tension_mNm"] = ys
        return sdf

    synth_dfs = {
        "tvae_demo": make_synth(fidelity=0.90, spurious_noise=0.1, seed=1),
        "gaussian_copula_demo": make_synth(fidelity=0.55, spurious_noise=0.2, seed=2),
        "ctgan_demo": make_synth(fidelity=0.25, spurious_noise=0.6, seed=3),
        "tabddpm_demo": make_synth(fidelity=0.45, spurious_noise=0.4, seed=4),
    }
    return real_df, synth_dfs, factors


if __name__ == "__main__":
    pd.set_option("display.width", 120)

    real_df, synth_dfs, factors = _build_illustrative_demo()

    interactions = [
        ("seawater_vv", "urea_pv"),
        ("urea_pv", "kh2po4_pv"),
        ("ammonium_sulfate_pv", "kh2po4_pv"),
    ]
    known_effects = [
        KnownEffect("seawater_vv:urea_pv", "Agua do mar x ureia (interacao negativa)"),
        KnownEffect("urea_pv:kh2po4_pv", "Ureia x KH2PO4 (interacao positiva)"),
        KnownEffect("ammonium_sulfate_pv:kh2po4_pv", "Sulfato de amonio x KH2PO4 (sinergia positiva)"),
        KnownEffect("seawater_vv", "Agua do mar (efeito principal negativo)"),
    ]

    summary, details = evaluate_generators(
        real_df=real_df,
        synth_dfs=synth_dfs,
        factors=factors,
        interactions=interactions,
        target="surface_tension_mNm",
        known_effects=known_effects,
    )

    print("\n=== ICD por gerador (demo ilustrativo, NAO sao os dados reais do estudo) ===\n")
    print(summary.to_string(index=False))

    print("\n=== Checklist efeito-a-efeito (S=Sinal, M=Magnitude, D=Detectavel) ===\n")
    print(checklist_table(details).to_string(index=False))

    print("\n=== Tabela de efeitos detalhada: TVAE (demo) ===\n")
    print(details["tvae_demo"].effects.to_string(index=False))
