# SAFE GITHUB BASELINE — Q1/Q2 Biosurfactant Synthetic Expansion v3

Generated: 2026-07-05 00:55:29

> **ATUALIZAÇÃO (2026-07-06):** a "Validated interpretation" original abaixo foi produzida
> por um pipeline com duas falhas metodológicas silenciosas, encontradas e corrigidas em
> `code/..._PEERFIX1.py` (ver `peer_review_investigation/DIAGNOSTICO_queda_utilidade_rerun_v4.md`).
> Leitura corrigida: **TVAE é o único gerador com utilidade não-negativa em ambos os
> cenários** (valor pontual sensível a seed/hiperparâmetro — tratado como achado no
> manuscrito, não escondido); Gaussian Copula, CTGAN e TabDDPM não mostram utilidade em
> nenhuma configuração testada. Resultados em `runs/exp_out_v6_PEERFIX1_doe0pct/` e
> `..._doe1pct/`. Os relatórios/figuras anteriores a esta correção foram movidos para
> `archive/pre_peerfix1_outputs/` — não usar como fonte de números.

This package is intended as the clean starting point before incorporating peer-review orchestration changes.

## Keep these code files

### Core pipeline / orchestration
- `code/expand_synthetic_enhanced_v10_TUNED_Q1Q2_FIXED25_TABDDPM_PATCHED_v9_Q1Q2_ARTIFACTS.py` (original; mantido para referência/diff)
- `code/expand_synthetic_enhanced_v10_TUNED_Q1Q2_FIXED25_TABDDPM_PATCHED_v9_Q1Q2_ARTIFACTS_PEERFIX1.py` **(usar este para qualquer nova execução)**
- `code/wrap_expand_for_report_v10_AUTOMATED_SKIPSAFE_VALIDFIX_PATCHED.py`
- `code/q1q2_bundle_from_expand_v10compat_SKIPSAFE_FIXED.py`
- `code/report_generator_v10_AUTOMATED_SKIPSAFE_v3.py`
- `code/ablation_from_expand_v10compat_SKIPSAFE_FIXED.py`

### Figures and consolidation
- `code/generate_q1q2_figures_STANDALONE.py`
- `code/generate_additional_q1q2_figures_FIXED.py`
- `code/q1q2_consolidate_reports.py`

### Optional compatibility/fallback
- `code/report_generator_v10_AUTOMATED_SKIPSAFE_v2_PATCHED.py`

## Validated interpretation (histórico — ver aviso de atualização acima)

- ~~Gaussian Copula: most stable utility–privacy balance.~~
- ~~TVAE: strong correlation/fidelity behavior, but high proximity risk under 1% DOE-noise.~~
- ~~CTGAN: favorable privacy/tail-risk behavior, but lower utility/fidelity.~~
- ~~TabDDPM: weakest utility and strongest degradation under noise.~~
- ~~No ranking inversion in the validated final results: `ΔRank = 0` for all generators.~~

**Interpretação atual (PEERFIX1):** TVAE é o único gerador com sinal de utilidade
não-negativo em ambos os cenários, mas instável a escolhas de protocolo de avaliação;
Gaussian Copula, CTGAN e TabDDPM não demonstram utilidade em nenhuma configuração testada;
nenhum gerador domina simultaneamente utilidade, fidelidade multivariada, concordância de
domínio (ICD) e risco de privacidade. Ver Seções 3.2–3.4 e 4.1 do manuscrito v3.

## Hard bounds decision

For this manuscript baseline, Biophysical Hard Bounds are not enforced inside the generative model.
They are retained as:
1. audit-only plausibility checks, and
2. a future-work extension for constraint-aware sampling/training.

This avoids reprocessing the heavy `expand` engine while preserving the scientific contribution.

## Recommended GitHub cleanup

Keep this package as the root reference and move older scripts/results to:
- `archive/`
- `deprecated/`
- `old_runs/`

Do not delete old material permanently until the peer-review revision is accepted.
