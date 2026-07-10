# MANUSCRIPT_METHODS_RESULTS_INSERTS_PEERFIX2

## Methods — Utility resampling paragraph
Replace the current note recommending LOOCV/k-fold with this implemented-method paragraph after running PEERFIX2:

> Because the real dataset contains only 20 observations, we replaced the single held-out split used in the diagnostic PEERFIX1 stage with resampling-based utility estimation. In the final validation layer, TSTR and TRTR were recomputed under repeated 5-fold cross-validation (10 repeats) [or LOOCV, if chosen], preserving the same-model delta Δ = TSTR − TRTR. R² was never computed on a single held-out point; instead, out-of-fold predictions were aggregated across all held-out observations within each repeat before computing R². For the strict fold-refit validation, synthetic datasets were generated only from the training subset of each fold, so that the held-out real observations were not used during synthetic-data generation.

## Methods — ICD aggregation paragraph

> The Domain-Grounded Concordance Index was computed for each independent synthetic realisation and then aggregated as mean ± 95% confidence interval across generator repeats, separately for the baseline and 1% DOE-noise sensitivity scenarios. This replaces the earlier single-realisation ICD table and makes domain-grounded validation statistically parallel to the utility analysis.

## Results — table placeholders
After the PEERFIX2 run, replace the older TSTR and ICD point estimates with:

- `outputs/peerfix2_final_tables/fold_refit_utility_best_models.csv`
- `outputs/peerfix2_final_tables/icd_aggregated_combined.csv`

## Submission cleanup
Remove before submission:

- all “NOTA DE REVISÃO” boxes;
- checklist blocks;
- references to temporary branch-only results;
- any sentence saying ICD is single-run;
- any README statement that Gaussian Copula is the valid final interpretation.
