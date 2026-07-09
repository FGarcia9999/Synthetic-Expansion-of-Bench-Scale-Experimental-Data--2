# Interpretação histórica (SUPERADA) — não usar como fonte de números

Este texto era a "Core interpretation" que aparecia no README principal antes de
2026-07-06. Foi produzida por um pipeline com duas falhas metodológicas silenciosas
(regularização do RandomForest ausente; TSTR treinado numa subamostra do sintético em
vez da expansão completa `n_synthetic`), identificadas e corrigidas no script PEERFIX1.

Ver `peer_review_investigation/DIAGNOSTICO_queda_utilidade_rerun_v4.md` para a
investigação completa, e o README principal / `SAFE_BASELINE_MANIFEST.md` para a
interpretação atual e válida.

## Texto original (histórico, não usar)

- Gaussian Copula showed the most stable utility–privacy balance.
- TVAE showed strong correlation/fidelity behavior, but higher proximity risk under 1% DOE-noise.
- CTGAN showed favorable privacy/tail-risk behavior, but weaker utility/fidelity.
- TabDDPM had the weakest utility and strongest degradation under noise.
- No validated ranking inversion was observed; the main effect is the magnitude of TSTR and the privacy trade-off.
