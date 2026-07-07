# Q1/Q2 Consolidated Report (Baseline 0% vs Sensitivity 1%)

Generated at (UTC): 2026-07-05 12:57:57Z

## Inputs

- Real dataset: `dados.csv`
- Target: `surface_tension_mNm`

Scenario output roots:
- Baseline scenario dir: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe0pct_tau010`
- Baseline bundle dir: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe0pct_tau010\bundle_q1q2`
- Sensitivity scenario dir: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe1pct_tau010`
- Sensitivity bundle dir: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe1pct_tau010\bundle_q1q2`

## Cross-scenario summary (utility, fidelity, privacy)

| Generator | Baseline TSTR (R²) | Sensitivity TSTR (R²) | Δ (Sens−Base) | Baseline |corr| (abs) | Sensitivity |corr| (abs) | Baseline DCR median | Sensitivity DCR median | Baseline frac(DCR<0.1) | Sensitivity frac(DCR<0.1) | Baseline MIA AUC | Sensitivity MIA AUC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ctgan | -0.910 | -0.772 | 0.138 | 0.297 | 0.176 | 1.290 | 1.338 | 0.036 | 0.064 | — | — |
| gaussian_copula | -0.230 | -0.244 | -0.015 | 0.513 | 0.511 | 1.157 | 1.161 | 0.193 | 0.193 | — | — |
| tabddpm | -1.085 | -1.969 | -0.884 | 0.537 | 0.393 | 1.497 | 1.548 | 0.207 | 0.243 | — | — |
| tvae | -0.254 | -0.341 | -0.087 | 0.418 | 0.325 | 0.000 | 0.336 | 0.579 | 0.436 | — | — |

## Scenario sections

### Baseline (0% DOE-noise)

- Scenario dir: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe0pct_tau010`
- Bundle dir: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe0pct_tau010\bundle_q1q2`
- Eval JSON: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe0pct_tau010\evaluation_results.json`
- Config JSON: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe0pct_tau010\experiment_config.json`

- Report: (not found in bundle dir; check runner logs)

#### Key figures

_(no figures found to embed; see diagnostics below)_

### Sensitivity (1% DOE-noise)

- Scenario dir: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe1pct_tau010`
- Bundle dir: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe1pct_tau010\bundle_q1q2`
- Eval JSON: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe1pct_tau010\evaluation_results.json`
- Config JSON: `C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2\runs\exp_out_v5_doe1pct_tau010\experiment_config.json`

- Report: (not found in bundle dir; check runner logs)

#### Key figures

_(no figures found to embed; see diagnostics below)_

## Notes

This consolidator **does not generate figures**. If the `bundle_q1q2/q1q2_figures/` folder does not contain `fig1_utility_comparison.*`, `fig2_privacy_comparison.*`, `fig3_fidelity_comparison.*`, please rerun the figure step (e.g., `generate_q1q2_figures_STANDALONE.py` or the bundle step with `--enable_q1q2_figures`) for each scenario.

