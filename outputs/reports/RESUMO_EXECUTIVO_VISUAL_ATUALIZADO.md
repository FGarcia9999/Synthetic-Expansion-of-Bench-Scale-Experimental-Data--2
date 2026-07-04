# 📊 RESUMO EXECUTIVO VISUAL - ARTIGO Q1/Q2 (ATUALIZADO)

**Atualizado em:** 2026-02-11 17:02:49  
**Fonte dos números:** `report_q1q2_consolidated.md` (Baseline 0% vs Sensitivity 1%) + `article_table.md` (métricas detalhadas do cenário Sensitivity)

## 🎯 EM UMA FRASE

> **Em small data, o Gaussian Copula se mantém o gerador mais “equilibrado” (utilidade estável + fidelidade moderada + baixo risco de proximidade), enquanto o TVAE entrega a melhor fidelidade multivariada, porém com risco de proximidade elevado — e que PIORA sob 1% de ruído DOE.**

---

## 📈 UTILIDADE DOWNSTREAM (TSTR em R²; maior é melhor)

```
BASELINE (0% DOE-noise)               SENSITIVITY (1% DOE-noise)
═══════════════════════               ═══════════════════════════
🥇 Gaussian:  -0.231                  🥇 Gaussian:  -0.247
🥈 TVAE:      -0.376                  🥈 TVAE:      -0.256
🥉 CTGAN:     -0.674                  🥉 CTGAN:     -0.953
4º TabDDPM:   -0.857                  4º TabDDPM:   -1.543
```

**Leitura correta:** todos os R² são negativos (tarefa difícil + small-n), então o foco é **comparativo e robustez** entre geradores.

---

## 🔬 FIDELIDADE MULTIVARIADA (|corr_of_corr|; mais perto de 1 = melhor)

- **TVAE**: 0.583 → **0.755** (melhora com ruído DOE)  
- **Gaussian Copula**: **0.513 → 0.513** (estável)  
- **TabDDPM**: 0.343 → 0.214 (piora)  
- **CTGAN**: 0.196 → 0.055 (colapso)

---

## 🔐 PRIVACIDADE / PROXIMIDADE (DCR; maior = melhor privacidade)

**Frac(DCR < 0.1)** e **DCR mediana**:

- **TVAE**: 0.464 → **0.593**  |  0.464 → **0.042**  (**piora forte; proximidade aumenta**)  
- **Gaussian Copula**: 0.193 → 0.193  |  1.157 → 1.156 (estável)  
- **CTGAN**: 0.043 → 0.029  |  1.386 → 1.370 (bom)  
- **TabDDPM**: 0.136 → 0.171  |  1.553 → 1.534 (bom, mas leve piora)

---

## ✅ PRINCIPAL INSIGHT (QUE VALE PARA O ARTIGO)

1) **Não houve “inversão” robusta do ranking de utilidade:** Gaussian continua na frente; TVAE aproxima sob DOE-noise, mas sem superar.  
2) **DOE-noise NÃO “protege” automaticamente privacidade:** no TVAE, o risco de proximidade **aumenta** (DCR mediana cai para 0.042 e frac(DCR<0.1) sobe para 59.3%).  
3) **Marginais ≠ multivariado:** CTGAN pode ir bem em KS (marginais), mas falha feio em correlações (estrutura).  
4) **Recomendação prática:** para small-n, **Gaussian Copula** como default “seguro”; **TVAE só com mitigação de privacidade** (ex.: filtro DCR/repulsão, DP, ou validações mais fortes).

---

- **Síntese visual (Figuras 4–5):** o trade-off privacidade–utilidade evidencia robustez do *Gaussian Copula* (pequenas variações), degradação de utilidade em *CTGAN/TabDDPM*, e melhora de utilidade do *TVAE* acompanhada de queda acentuada de privacidade (DCR mediana < 0,1). O ranking por utilidade se mantém estável (ΔRank = 0), mas as magnitudes de TSTR mudam de forma relevante.
- **Conexão com o DOE real:** recomenda-se explicitar, na Discussão, como os achados sintéticos se alinham (ou não) às relações físico-químicas do processo (efeitos principais/interações do planejamento fatorial, limites físicos da tensão superficial) para fortalecer a aceitação do modelo do biossurfactante.
