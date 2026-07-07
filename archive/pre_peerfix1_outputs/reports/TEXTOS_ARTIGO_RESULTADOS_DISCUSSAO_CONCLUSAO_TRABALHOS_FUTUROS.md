# Textos revisados para o artigo (Resultados/Discussão, Conclusão e Trabalhos Futuros)

**Atualizado em:** 2026-02-11 17:02:49  
**Arquivos-base (resultados):** `report_q1q2_consolidated.md`, `article_table.md`, `comprehensive_report.md`, `experiment_config.json`.  
**Geradores avaliados:** Gaussian Copula, CTGAN, TVAE, TabDDPM.  
**Cenários:** Baseline (0% DOE-noise) e Sensitivity (1% DOE-noise).  
**Métrica de privacidade:** DCR com τ = 0.1.

---

## 1. Resultados e Discussão (Português – pronto para colar)

### 1.1 Utilidade downstream (TSTR/TRTR; R² signed)
A utilidade foi avaliada por **TSTR (Train on Synthetic, Test on Real)**, reportada como **R² signed** (maior é melhor), e complementada por comparações com **TRTR (Train on Real, Test on Real)** para reduzir leituras infladas em *small-n*. Em ambos os cenários, o **Gaussian Copula apresentou o melhor TSTR**: **−0.231** no baseline e **−0.247** na sensibilidade, evidenciando robustez a 1% de ruído DOE. O **TVAE** ficou em segundo lugar, mas aproximou-se do Gaussian sob DOE-noise (**−0.376 → −0.256**). Em contraste, **CTGAN** e **TabDDPM** degradaram de forma mais acentuada com DOE-noise (CTGAN **−0.674 → −0.953**; TabDDPM **−0.857 → −1.543**), sugerindo maior sensibilidade dessas abordagens à perturbação de entradas.

Como os valores de R² são negativos em todos os casos (tarefa difícil e/ou conjunto real pequeno), a interpretação deve ser **comparativa**, enfatizando ordenação entre geradores e estabilidade entre cenários, e não valores absolutos. No cenário Sensitivity, a análise *same-model* (RF) indica que **TVAE (+0.371) e Gaussian (+0.351)** possuem Δ(TSTR−TRTR) positivos no mesmo regressor, sugerindo que, nessa configuração, treinar no sintético pode ser comparável ou superior a treinar no real (sob o mesmo modelo). Já **CTGAN (−0.339)** e **TabDDPM (−0.902)** apresentam deltas negativos, indicando prejuízo relativo quando se compara treino em sintético versus treino em real no mesmo regressor.

### 1.2 Fidelidade multivariada (preservação de dependências)
A preservação de dependências foi sintetizada por **|corr_of_corr|** (magnitude da correlação entre as matrizes de correlação real vs. sintética). Os resultados favorecem consistentemente o **TVAE**, que melhora com DOE-noise (**0.583 → 0.755**), indicando maior capacidade de reter estrutura multivariada. O **Gaussian Copula** permanece estável (**0.513 → 0.513**), sugerindo fidelidade moderada e robusta. Por outro lado, o **TabDDPM** reduz fidelidade (**0.343 → 0.214**) e o **CTGAN** colapsa (**0.196 → 0.055**) no cenário de sensibilidade, o que é compatível com geração que reproduz marginais mas falha em dependências.

Esse contraste é relevante porque, em small-n, bons indicadores univariados podem não se traduzir em realismo multivariado. No cenário Sensitivity, por exemplo, o CTGAN exibiu KS médio relativamente baixo (estatística menor), porém apresentou a pior preservação de correlações, reforçando que avaliar apenas marginais pode superestimar a qualidade do sintético.

### 1.3 Privacidade / proximidade (DCR; τ = 0.1)
O risco de proximidade foi medido por **DCR (Distance to Closest Record)**, reportando a **mediana do DCR** (maior = melhor privacidade) e a **fração de registros com DCR < τ** (menor = melhor). Os resultados evidenciam um ponto crítico:

- **TVAE:** alto risco de proximidade já no baseline (**frac = 0.464; DCR med = 0.464**) e risco ainda maior sob DOE-noise (**frac = 0.593; DCR med = 0.042**).
- **Gaussian Copula:** estabilidade (**frac = 0.193 → 0.193; DCR med = 1.157 → 1.156**).
- **CTGAN:** bom perfil de privacidade (**frac = 0.043 → 0.029; DCR med ≈ 1.386 → 1.370**).
- **TabDDPM:** bom DCR mediano (**1.553 → 1.534**), com fração sob τ moderada (**0.136 → 0.171**).

A principal implicação é que **DOE-noise é um teste de robustez, não um mecanismo de privacidade**. Em particular, o comportamento do TVAE mostra que uma perturbação leve pode não reduzir proximidade e, em alguns casos, expor ainda mais tendências de sobreajuste. Para aplicação em contextos sensíveis, o TVAE deve ser combinado com mitigação explícita (p.ex., filtro por DCR/repulsão, treinamento com DP, ou validações adicionais).

### 1.4 Síntese interpretativa (trade-offs)
Os resultados apontam um trade-off clássico em dados pequenos:

- **TVAE:** melhor fidelidade multivariada e utilidade alta (2º lugar e quase empate sob DOE-noise), porém **maior risco de proximidade**.
- **Gaussian Copula:** melhor utilidade e robustez, fidelidade moderada e estável, com **risco de proximidade controlado** — melhor compromisso geral.
- **CTGAN:** marginais potencialmente aceitáveis, mas baixa fidelidade multivariada e queda forte de utilidade sob DOE-noise.
- **TabDDPM:** perfil de privacidade mais favorável, porém com custo elevado de utilidade downstream, especialmente sob DOE-noise.



### 1.5 Linking synthetic findings to the experimental biosurfactant process (Discussion add-on)
The original dataset is rooted in a **small experimental design (DOE) for biosurfactant production**, where surface tension is measured as the primary response. In this setting, the response is driven by **strong main effects and interactions** (e.g., nutrient balance and salinity/medium composition), and measurement variability is unavoidable (e.g., instrument repeatability and operational fluctuations). Therefore, the Sensitivity scenario (1% DOE-noise) is not merely a synthetic “stress test”; it is a proxy for the **realistic error budget** expected in laboratory/bench-scale biosurfactant campaigns.

Within this experimental framing, the key message from Figures 4–5 is that **robust utility does not automatically imply safe privacy**, and vice‑versa. Under 1% DOE-noise, the **generator ranking remains unchanged**, but utility shifts materially for some models. Gaussian Copula is essentially stable (ΔTSTR ≈ −0.015), which is consistent with the idea that a low‑complexity dependence model can be sufficient to reproduce the dominant DOE structure in small‑n regimes. Conversely, the TVAE shows a utility gain (ΔTSTR ≈ +0.120) while exhibiting a **severe proximity collapse** (median DCR dropping below the risk threshold), suggesting that a high‑capacity model may still generate near‑replicas when the training support is narrow.

For **process‑model acceptance**, the practical implication is that synthetic data should be positioned as a *supporting asset* rather than a replacement for experimental evidence. A defensible pathway is to demonstrate that synthetic augmentation preserves the **direction and relative magnitude of DOE effects** observed experimentally. Concretely, the manuscript can strengthen its applied contribution by adding: (i) a **real vs. synthetic main‑effects/interaction consistency check** (e.g., factorial/ANOVA contrasts or a linear model with interactions on real DOE vs. synthetic DOE), (ii) domain‑informed plausibility constraints (surface tension bounds, monotonic trends where applicable), and (iii) an uncertainty view (e.g., bootstrap intervals on effect estimates). If the synthetic data reproduces the experimental effect structure while improving model stability, it becomes a credible component of a digital workflow for biosurfactant process modeling.

---

## 2. Conclusion (English – manuscript-ready)

We evaluated four tabular synthetic data generators (Gaussian Copula, CTGAN, TVAE, and TabDDPM) under two experimental settings: a baseline (0% DOE-noise) and a robustness test with mild perturbation (1% DOE-noise). Across both scenarios, **Gaussian Copula** provided the most balanced performance for small experimental data. It achieved the best downstream utility (TSTR, signed R²) in both conditions (−0.231 in the baseline; −0.247 under DOE-noise) and maintained stable multivariate structure (|corr_of_corr|≈0.513) with controlled proximity risk (DCR median ≈ 1.156–1.157; frac(DCR<0.1)=0.193).

**TVAE** consistently delivered the strongest multivariate fidelity and further improved under DOE-noise (|corr_of_corr| 0.583→0.755), and it nearly matched Gaussian Copula in utility under the sensitivity setting (−0.256). However, TVAE also exhibited **substantially higher proximity risk**, which **worsened** when DOE-noise was introduced (DCR median 0.464→0.042; frac(DCR<0.1) 0.464→0.593). This demonstrates that mild DOE perturbations should be interpreted as robustness stress-tests rather than privacy mechanisms. 

Overall, these results indicate that, for small datasets, simpler distributional models can outperform more complex generators in robustness and practical downstream utility, while high-fidelity generators require explicit privacy controls before deployment.

---

## 3. Future Work (English – manuscript-ready)

Future work should extend this study in four directions. First, incorporate **explicit privacy mechanisms**—such as differentially private training, PATE-style aggregation, or post-generation safeguards (e.g., DCR-based filtering and repulsion)—and report privacy–utility trade-off frontiers. Second, broaden utility evaluation beyond a single regression target by including multiple tasks (multi-output regression and classification), domain constraints, and uncertainty reporting (e.g., confidence intervals for TSTR/TRTR deltas under repeated splits). Third, expand fidelity diagnostics for mixed-type tabular data, including dependence measures beyond correlations (e.g., mutual information proxies or copula-based dependence tests), and align metrics with application-relevant invariants. Fourth, test robustness across a wider perturbation spectrum (DOE-noise levels, outlier regimes, and scaling choices) to characterize stability regions and failure modes, enabling principled generator selection for small experimental datasets.

---

## 4. Referências bibliográficas acadêmicas (para fundamentar métodos/métricas)

- Shokri, R. et al. (2017). **Membership Inference Attacks Against Machine Learning Models**. *IEEE Symposium on Security and Privacy*.  
- Stadler, T., Oprisanu, B., & Troncoso, C. (2020). **Synthetic Data — Anonymisation Groundhog Day**. *USENIX Security*.  
- Xu, L. et al. (2019). **Modeling Tabular Data using Conditional GAN** (CTGAN). *NeurIPS Workshop / arXiv*.  
- Kingma, D. P., & Welling, M. (2014). **Auto-Encoding Variational Bayes** (VAE). *ICLR*.  
- Arjovsky, M., Chintala, S., & Bottou, L. (2017). **Wasserstein GAN**. *ICML*.  
- Jordon, J., Yoon, J., & van der Schaar, M. (2018). **PATE-GAN**. *ICLR Workshop / arXiv*.


---

### Captions (English) for Figures 4–5 (ready to paste)

**Figure 4.** Privacy–utility trade-off across Baseline (0% DOE noise; circles) and Sensitivity (1% DOE noise; triangles) scenarios. Utility is measured by signed TSTR R² (closer to 0 is better), and privacy by the median DCR distance (higher is safer). Arrows connect each generator’s Baseline→Sensitivity shift. The dashed red line marks the proximity-risk threshold (DCR = 0.1), and the dashed vertical line indicates perfect utility (TSTR = 0). Under realistic noise, Gaussian Copula remains stable, CTGAN and TabDDPM lose utility with minor privacy changes, and TVAE improves utility but exhibits a sharp privacy drop, with median DCR falling below the risk threshold.

**Figure 5.** Utility and ranking summary under Baseline (0% DOE) and Sensitivity (1% DOE) scenarios. Values are signed TSTR R² with ranks (1 = best). ΔTSTR is computed as Sensitivity − Baseline (positive indicates utility improvement, i.e., less negative/closer to zero); ΔRank denotes rank change. Rankings remain unchanged (ΔRank = 0), but utility shifts: TVAE shows moderate improvement (+0.120), whereas CTGAN (−0.278) and TabDDPM (−0.686) degrade markedly. Gaussian Copula changes minimally (−0.015), indicating robustness to realistic DOE noise.

