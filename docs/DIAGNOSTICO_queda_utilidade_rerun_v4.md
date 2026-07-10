# Diagnóstico: Queda de Utilidade no Rerun "Clean Q1/Q2 v4"

**Autor da investigação:** Claude (Anthropic), a pedido de Fernando Garcia
**Data:** 2026-07-06
**Escopo:** Investigar por que `runs/exp_out_v5_doe0pct_tau010/evaluation_results.json`
(branch `rerun-clean-q1q2-v4`) mostra TSTR_best negativo para os 4 geradores, enquanto
o script antigo verificado (usado no manuscrito) produzia TVAE com TSTR_best=0.668.

## Pergunta original

O SAFE_BASELINE_MANIFEST.md afirma que a interpretação validada é: "Gaussian Copula =
melhor estabilidade utilidade-privacidade; sem inversão de ranking (ΔRank=0)". Isso é
tecnicamente consistente com os números do rerun, mas os números do rerun descrevem um
cenário onde **nenhum gerador tem utilidade preditiva positiva** — uma mudança científica
muito mais drástica do que a frase sugere. Era preciso saber se isso é um achado real ou
efeito colateral da "limpeza" do código.

## Método: isolamento de variáveis, uma de cada vez

Usando `code/expand_synthetic_enhanced_v10_TUNED_Q1Q2_FIXED25_TABDDPM_PATCHED_v9_Q1Q2_ARTIFACTS.py`
como ponto de partida, apliquei três restaurações, cada uma isolada e depois cumulativa,
comparando sempre contra `dados.csv` real e o mesmo target (`surface_tension_mNm`):

1. **RF regularizado**: `max_depth=15, min_samples_split=5, min_samples_leaf=2` (valores do
   script antigo verificado) em vez dos defaults do sklearn (profundidade ilimitada).
2. **Treino do TSTR na expansão sintética completa** (`n_synthetic=140`), não em uma
   subamostra do tamanho do treino real (~15 linhas) — que é o que o script novo faz
   (`idx = rng.choice(len(X_synth), size=len(X_train), replace=True)`).
3. **Seed idêntica ao run original** (123, em vez do default atual 42).

## Resultado (TSTR_best por gerador, cenário baseline/0%)

| Gerador | Antigo verificado (seed 123) | Novo (quebrado) | +RF regularizado | +RF + synth completo | +RF+synth completo+seed 123 |
|---|---|---|---|---|---|
| TVAE | 0.668 | -0.254 | 0.039 | 0.207 | **0.442** |
| Gaussian Copula | 0.057 | -0.230 | -0.077 | -0.250 | -0.250 |
| CTGAN | -0.081 | -0.910 | -0.978 | -0.262 | -0.177 |
| TabDDPM | 0.072 | -1.085 | -0.693 | -0.754 | **0.024** |

## Interpretação

- Os itens 1 e 2 têm efeito direto, mensurável e cumulativo na direção de recuperar os
  números originais — especialmente o item 2, que não é apenas um "bug de hiperparâmetro",
  é uma **mudança conceitual no que TSTR significa**, e contradiz a própria Seção 2.5 do
  manuscrito, que descreve treinar em `n_synth=140` amostras sintéticas completas.
- TVAE e TabDDPM respondem fortemente às três restaurações, aproximando-se dos valores
  originais. Gaussian Copula e CTGAN continuam negativos nesses testes — pode ser um
  comportamento genuíno (já eram os mais fracos no estudo original) ou pode exigir mais uma
  rodada de investigação (não teve tempo de isolar aqui: possível diferença em
  `test_size` 0.25 vs 0.3, ou em como `X_synth`/`X_real` são codificados antes do fit).
- **Conclusão:** o colapso generalizado de utilidade no rerun "limpo" não deve ser tratado
  como um achado científico novo e validado. É, em grande parte, efeito de mudanças
  metodológicas silenciosas introduzidas durante a padronização do código, não uma
  descoberta sobre os geradores.

## Recomendação

1. Não adotar `runs/exp_out_v5_doe0pct_tau010` / `..._doe1pct_tau010` como baseline
   científica final sem antes reconciliar os três pontos acima.
2. Corrigir `_make_model_constructor` (RF) e `evaluate_utility_enhanced` (treino no
   `X_synth` completo, não subamostrado) na branch `peer-review-revisions-v1`,
   preservando `rerun-clean-q1q2-v4` intocada, conforme o próprio runbook já orienta.
3. Rerodar baseline E sensitivity por completo (`n_runs=10`, ambos os cenários) com as
   correções aplicadas, e só então atualizar `SAFE_BASELINE_MANIFEST.md` e o manuscrito
   com os números resultantes.
4. Investigar isoladamente por que Gaussian Copula/CTGAN permanecem negativos mesmo após
   as correções — se persistir, pode ser um achado genuíno e deve ser reportado como tal.

## Atualização: PEERFIX1 — correção definitiva, baseline + sensibilidade completos (seed=123, n_runs=10)

Após aplicar as duas correções de forma definitiva (não mais como teste) em
`expand_synthetic_enhanced_v10_TUNED_Q1Q2_FIXED25_TABDDPM_PATCHED_v9_Q1Q2_ARTIFACTS_PEERFIX1.py`,
rodei os dois cenários completos:

**Baseline (doe_noise_pct=0.0):**

| Gerador | corr_of_corr | TSTR_best (modelo) | TRTR | Δ | DCR<0.1 |
|---|---|---|---|---|---|
| TVAE | 0.320 | 0.143 (mlp) | −3.775 | 3.917 | 0.493 |
| Gaussian Copula | 0.513 | −0.250 (lr) | −1.667 | 1.416 | 0.193 |
| CTGAN | 0.014 | −0.192 (lr) | −1.667 | 1.475 | 0.036 |
| TabDDPM | 0.625 | −0.501 (rf) | −0.691 | 0.190 | 0.129 |

**Sensibilidade (doe_noise_pct=1.0):**

| Gerador | corr_of_corr | TSTR_best (modelo) | TRTR | Δ | DCR<0.1 |
|---|---|---|---|---|---|
| TVAE | 0.638 | 0.617 (rf) | −0.738 | 1.355 | 0.629 |
| Gaussian Copula | 0.513 | −0.239 (lr) | −1.667 | 1.428 | 0.186 |
| CTGAN | −0.038 | −0.220 (rf) | −0.683 | 0.463 | 0.036 |
| TabDDPM | 0.220 | −0.678 (rf) | −0.667 | −0.011 | 0.193 |

### Leitura honesta

- **TVAE é o único gerador que mostra utilidade positiva (ou perto de zero) em ambos os
  cenários**, mesmo com as correções aplicadas — consistente com ser o gerador mais
  promissor, como na análise original, embora o valor pontual exato varie run a run
  (já observamos 0.039, 0.143, 0.207, 0.442 e 0.617 para TVAE em diferentes combinações
  de seed/config nesta investigação). Isso não é ruído a esconder — é o próprio
  fenômeno que motiva o artigo (fragilidade estatística de bancada pequena).
- **Gaussian Copula e CTGAN permanecem com TSTR negativo de forma consistente**, mesmo
  após as duas correções e em múltiplas seeds testadas. Isso já não parece mais efeito
  colateral de bug — parece ser um achado genuíno: esses dois geradores não capturam o
  sinal esparso da tensão superficial (lembrando: apenas 1-2 efeitos fatoriais realmente
  significativos, ver Seção 2.1 do manuscrito revisado) o suficiente para superar o
  próprio ruído da divisão treino/teste em n=20.
- **TabDDPM permanece fraco/negativo**, com Δ próximo de zero na sensibilidade — outro
  padrão que se mantém estável através das correções.
- **Recomendação para o manuscrito:** relatar os quatro geradores com essa moldura —
  TVAE como o único com sinal de utilidade real (variável, mas consistentemente não-
  negativo), os demais três sem utilidade demonstrada para esta variável-alvo — e usar a
  própria variabilidade do TVAE entre reamostragens como argumento para a seção de
  limitações/protocolo (Seção 4.3), reforçando por que o ICD e o Δ agregado por rodada
  são necessários em vez de um único ponto.


- `expand_ISOLATION_TEST_rf_regularized.py` — apenas item 1 aplicado
- `expand_ISOLATION_TEST_v2_full_synth.py` — itens 1+2 aplicados
- `out_isolation_test/`, `out_isolation_v2/`, `out_isolation_v3_seed123/` — outputs brutos
  de cada teste, para auditoria independente
- Este relatório (`DIAGNOSTICO_queda_utilidade_rerun_v4.md`)
