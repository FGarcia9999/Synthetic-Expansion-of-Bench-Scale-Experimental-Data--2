# 🎓 RELATÓRIO FINAL DE APROVAÇÃO Q1/Q2 (ATUALIZADO)

**Atualizado em:** 2026-02-11 17:02:49  
**Projeto:** Synthetic Data Generation for Small Experimental Datasets  
**Status:** ✅ **APTO PARA SUBMISSÃO** (com textos ajustados aos novos números)

---

## 📊 EXECUTIVE SUMMARY (ATUALIZADO)

- **Utilidade (TSTR, R² signed):** Gaussian mantém o melhor desempenho em ambos os cenários (**-0.231** baseline; **-0.247** sensitivity). TVAE fica muito próximo sob DOE-noise (**-0.256**), mas sem ultrapassar o Gaussian.  
- **Fidelidade multivariada (|corr_of_corr|):** TVAE é o melhor e melhora com DOE-noise (**0.583 → 0.755**). Gaussian é estável (**0.513 → 0.513**). CTGAN colapsa (**0.196 → 0.055**).  
- **Privacidade (DCR):** TVAE exibe **alto risco de proximidade** e esse risco **piora** com DOE-noise (**DCR med 0.464 → 0.042; frac(DCR<0.1) 0.464 → 0.593**). Os demais geradores mantêm DCR mediana > 1.15 e frac(DCR<0.1) ≤ 0.193.

**Conclusão operacional:** em small data, **Gaussian Copula** é o melhor compromisso utilidade–fidelidade–privacidade; **TVAE** é “best-in-fidelity” porém “worst-in-privacy” sem mitigação explícita.

---

## 🎯 DESCOBERTAS PRINCIPAIS (ATUALIZADAS)

### 1) ROBUSTEZ DO GAUSSIAN + “QUASE EMPATE” COM TVAE EM UTILIDADE (sob DOE-noise)

```
Baseline (0% DOE-noise)            Sensitivity (1% DOE-noise)
════════════════════════           ═══════════════════════════
Gaussian:  -0.231 (1º)             Gaussian:  -0.247 (1º)
TVAE:      -0.376 (2º)             TVAE:      -0.256 (2º, muito próximo)
CTGAN:     -0.674 (3º)             CTGAN:     -0.953 (3º)
TabDDPM:   -0.857 (4º)             TabDDPM:   -1.543 (4º)
```

**Leitura:** sob 1% DOE-noise, há degradação forte em CTGAN/TabDDPM, enquanto Gaussian e TVAE se mantêm no topo.

### 2) “Fidelidade alta” pode custar privacidade (TVAE)

- TVAE melhora correlações (0.583 → 0.755), mas aproxima perigosamente dos registros reais (DCR med 0.464 → 0.042).  
- Resultado prático: **sem filtro/repulsão/DP, TVAE fica difícil de justificar para uso sensível**.

### 3) CTGAN mostra o alerta clássico: marginais boas não garantem estrutura

Mesmo quando estatísticas univariadas são aceitáveis, a preservação de dependências pode falhar (corr_of_corr muito baixo no cenário sensibilidade).

---

## ✅ AJUSTES DE ESCRITA RECOMENDADOS (PARA O MANUSCRITO)

- Retirar qualquer menção a “inversão robusta de ranking” (não suportada pelos números atuais).  
- Trocar “memorização total (DCR=0.000)” por **“alto risco de proximidade, agravado por DOE-noise”**.  
- Enfatizar que **DOE-noise não é mecanismo de privacidade**, e que a mitigação deve ser explícita.

---

## Figuras adicionais para o artigo (Fig. 4–5)

As Figuras 4–5 foram adicionadas para sintetizar (i) o trade-off privacidade–utilidade e (ii) a estabilidade de ranking sob ruído realista de DOE.

**Captions (English):**

- **Figure 4.** Privacy–utility trade-off across Baseline (0% DOE noise; circles) and Sensitivity (1% DOE noise; triangles) scenarios. Utility is measured by signed TSTR R² (closer to 0 is better), and privacy by the median DCR distance (higher is safer). Arrows connect each generator’s Baseline→Sensitivity shift. The dashed red line marks the proximity-risk threshold (DCR = 0.1), and the dashed vertical line indicates perfect utility (TSTR = 0). Under realistic noise, Gaussian Copula remains stable, CTGAN and TabDDPM lose utility with minor privacy changes, and TVAE improves utility but exhibits a sharp privacy drop, with median DCR falling below the risk threshold.

- **Figure 5.** Utility and ranking summary under Baseline (0% DOE) and Sensitivity (1% DOE) scenarios. Values are signed TSTR R² with ranks (1 = best). ΔTSTR is computed as Sensitivity − Baseline (positive indicates utility improvement, i.e., less negative/closer to zero); ΔRank denotes rank change. Rankings remain unchanged (ΔRank = 0), but utility shifts: TVAE shows moderate improvement (+0.120), whereas CTGAN (−0.278) and TabDDPM (−0.686) degrade markedly. Gaussian Copula changes minimally (−0.015), indicating robustness to realistic DOE noise.
