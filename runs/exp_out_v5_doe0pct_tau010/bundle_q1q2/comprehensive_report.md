# Biosurfactant Synthetic Expansion - Baseline

Scenario: **Baseline 0% DOE-noise**
Generated at: 2026-07-05 09:54:19

## Experimental and computational setup

- Target variable: `surface_tension_mNm`
- Number of synthetic samples per generator: `140`
- Number of repeated evaluations: `10`
- DOE noise enabled: `True`
- DOE noise percentage: `0.0`
- DCR threshold tau: `0.1`

## Main performance table

| Generator | Best model | TSTR R2 | TRTR R2 | Median DCR | DCR<0.1 (%) | Corr-of-corr |
|---|---:|---:|---:|---:|---:|---:|
| gaussian_copula | rf | -0.230 | -0.615 | 1.157 | 19.3 | NA |
| tvae | rf | -0.254 | -0.652 | 0.000 | 57.9 | NA |
| ctgan | rf | -0.910 | -0.642 | 1.290 | 3.6 | NA |
| tabddpm | rf | -1.085 | -0.642 | 1.497 | 20.7 | NA |

## Results summary

The best utility result was obtained by **gaussian_copula**, with TSTR signed R2 = **-0.230** using the `rf` model.

The results confirm that synthetic-data quality in small-n bioprocess datasets should not be judged by a single metric. Utility, proximity to real records, and preservation of correlation structure describe complementary aspects of model behavior.

In this biosurfactant dataset, the most useful generators are those that preserve predictive behavior for surface tension while avoiding excessive proximity to the original DOE records. This supports the use of synthetic expansion as a controlled proxy for process-model exploration, provided that physical and chemical plausibility is interpreted together with statistical metrics.

## Figure references

- Figure 1: Utility comparison based on TSTR signed R2.
- Figure 2: Median DCR comparison.
- Figure 3: Fidelity comparison based on correlation preservation.

## Notes for manuscript integration

These outputs are intended to support the Results and Discussion sections of the manuscript. For the final article, captions should clarify that DCR median and DCR risk fraction are different privacy/proximity indicators.
