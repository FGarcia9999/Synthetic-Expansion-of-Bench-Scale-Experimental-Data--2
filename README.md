# Synthetic Expansion of Bench-Scale Experimental Data — Safe Q1/Q2 Baseline v3

> **ATUALIZAÇÃO (2026-07-06, branch `peer-review-revisions-v1`): a interpretação "Core
> interpretation" abaixo foi produzida por um pipeline com duas falhas metodológicas
> silenciosas (regularização do RandomForest ausente; TSTR treinado numa subamostra do
> sintético em vez da expansão completa `n_synthetic`). Após correção (script
> `code/..._PEERFIX1.py`), a leitura passa a ser: **TVAE é o único gerador com sinal de
> utilidade não-negativo em ambos os cenários** (mas com valor pontual sensível a
> seed/hiperparâmetros — ver diagnóstico); Gaussian Copula, CTGAN e TabDDPM não mostram
> utilidade em nenhuma configuração testada. Ver
> `peer_review_investigation/DIAGNOSTICO_queda_utilidade_rerun_v4.md` para a investigação
> completa (isolamento de variáveis, tabela comparativa) antes de citar a interpretação
> abaixo como válida. Resultados corrigidos em `runs/exp_out_v6_PEERFIX1_doe0pct/` e
> `runs/exp_out_v6_PEERFIX1_doe1pct/`.**

This repository stores the validated safe baseline for the biosurfactant synthetic data expansion workflow.

The active baseline is documented in `SAFE_BASELINE_MANIFEST.md`. Older/experimental files should remain outside the active workflow or be moved to `archive/`, `deprecated/`, or `old_runs/`.

Core interpretation of the validated baseline **(superseded — see update notice above)**:

- Gaussian Copula showed the most stable utility–privacy balance.
- TVAE showed strong correlation/fidelity behavior, but higher proximity risk under 1% DOE-noise.
- CTGAN showed favorable privacy/tail-risk behavior, but weaker utility/fidelity.
- TabDDPM had the weakest utility and strongest degradation under noise.
- No validated ranking inversion was observed; the main effect is the magnitude of TSTR and the privacy trade-off.

Start with `docs/RUNBOOK_SAFE_BASELINE.md` to reproduce the validated figures and consolidated reports.

