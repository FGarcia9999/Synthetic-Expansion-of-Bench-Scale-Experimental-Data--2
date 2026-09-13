# PEERFIX-Core v1.0 — Gate 0.1 Reproducibility Lineage Audit

Date: 2026-09-13
Status: **HISTORICAL LINEAGE INCOMPLETE — CLEAN REPROCESSING REQUIRED BEFORE FREEZE**

## Scope
This audit traces the execution lineage behind the current PEERFIX2/C&CE manuscript-facing results before PEERFIX-Core v1.0 is frozen. The purpose is not to preserve a preferred historical result, but to identify which parts of the current evidence are reproducible, which are only documented at summary level, and what must be rerun cleanly.

## 1. Current publication-facing result set
The clean branch `cce-v26-zenodo-metadata` identifies `outputs/peerfix2/Table_2_Utility_repeated_kfold_best_models.csv` as the submission-facing utility table. That CSV explicitly reports `n_repeats = 5` for all generator/scenario rows. Its values match the current late-stage manuscripts: Gaussian Copula has the highest mean TSTR in both scenarios; CTGAN has positive same-model Delta despite negative absolute TSTR; TVAE leads ICD rather than utility.

The clean ICD table reports 10 full synthetic realisations per generator/scenario. Thus the publication-facing design currently combines:

- Utility: repeated 5-fold CV x 5 repeats.
- ICD: 10 full synthetic realisations per generator/scenario.

## 2. Historical runbook intended 10 utility repeats
The historical `docs/PIPELINE_ORQUESTRACAO_PEERFIX2.md` at commit `4ac9fdf8585a4592d7214aa99df1b5fffc07fa1d` specifies:

- `--cv repeated_kfold`
- `--n_splits 5`
- `--n_repeats_cv 10`
- `--n_generator_repeats 10`
- `--n_synthetic 140`
- master seed `123`

It therefore documents an intended 5-fold x 10-repeat utility protocol, not the final manuscript-facing 5-fold x 5-repeat protocol.

## 3. A separate strict 10-repeat execution exists
A preserved `run_metadata.json` records a strict no-leakage repeated-k-fold execution with:

- `n_splits = 5`
- `n_repeats = 10`
- `n_synth = 140`
- seed `123`
- synthetic generation restricted to the real training fold
- DCR reference restricted to the training fold
- R2 calculated after out-of-fold prediction aggregation within each repeat

The associated report contains 10 scored repeats and produces utility values that differ from the current five-repeat manuscript table. Therefore the discrepancy is not a documentation typo: at least two distinct strict repeated-k-fold executions/protocol states existed.

## 4. Exact lineage of the current five-repeat Table 2 is incomplete
The current clean table is internally coherent with the current manuscript and explicitly records five repeats. However, the repository does not currently preserve a complete, uniquely linked chain:

`canonical config -> exact generator-refit code -> per-fold raw outputs -> repeat-level summaries -> final Table 2`

for the five-repeat result set.

The historical runbook references `q1q2_peerfix2_orchestrate.py` and `q1q2_peerfix2_collect_fold_refit.py`, but these execution scripts are not present in the current clean/main tree in a way that uniquely reconstructs the final five-repeat run. The cleanup commit intentionally removed large historical/intermediate material, preserving summary outputs but weakening execution lineage.

## 5. `q1q2_peerfix2_cv_icd.py` must not become the utility engine of PEERFIX-Core
A preserved version of `q1q2_peerfix2_cv_icd.py` defaults to 10 repeated-k-fold repeats, but its utility audit loads an already-exported synthetic realisation and then resamples the downstream prediction problem. The script itself warns that this is only a downstream-model resampling audit unless the supplied synthetic directories came from fold-specific generator refits.

Therefore this script is acceptable for ICD/resampling audit functions, but it is **not** by itself sufficient evidence of the Core no-leakage utility rule. The PEERFIX-Core utility engine must explicitly refit each generator inside every real-training fold.

## 6. Downstream model-set lineage is also inconsistent
The current late-stage manuscript describes four downstream models:

- Linear Regression
- regularised Random Forest
- MLP
- Gradient Boosting

A preserved strict 10-repeat `run_metadata.json`, however, lists only `lr`, `ridge`, and `rf`. Earlier manuscript states also mention optional XGBoost. This confirms that model-set history changed during development and must be frozen explicitly rather than inferred from historical runs.

## 7. Canonical derivation dataset
The clean branch contains a 20-run full 2^4 factorial plus four centre-point observations in `data/dados.csv`, with factors:

- seawater_vv
- urea_pv
- ammonium_sulfate_pv
- kh2po4_pv

and target `surface_tension_mNm`.

SHA-256 of the exact CSV text audited at this checkpoint:

`d7420eaa5d1c45f1287e12af5737893b244a6302beecab0da35a2b464d040001`

This dataset may serve as the PEERFIX2 derivation dataset for the clean rerun, subject to the separate provenance/licensing record.

## Gate 0.1 decision
**FAIL for exact historical reproducibility of the current five-repeat result lineage.**

This is not a failure of the scientific program. It means PEERFIX-Core v1.0 must not be frozen by copying a historical state whose exact execution chain cannot be uniquely reconstructed.

**GO for controlled clean reprocessing before freeze.**

## Recommended remediation
Before any external dataset is processed:

1. Build a new canonical `PEERFIX_CORE_v1.0_PRE_FREEZE.yaml`.
2. Reconstruct a minimal Core utility engine in which generator fitting occurs inside every real-training fold.
3. Freeze deterministic seed derivation for split, generator and downstream model.
4. Freeze the downstream model set.
5. Use 5 folds x **10 repeats** as the proposed primary utility protocol because it matches the original stricter runbook intent and provides a larger repeated-CV stability sample.
6. Retain the first 5 repeats as a predefined historical-comparability sensitivity analysis against the manuscript-facing five-repeat results.
7. Keep 10 full synthetic realisations per generator/scenario for ICD, with fixed seeds 123–132 unless the pre-freeze config documents another deterministic seed map.
8. Preserve every per-fold prediction, generator seed, failure, elapsed status, and output hash in the new run manifest.
9. Do not tune Core decisions after viewing external candidate results.

## Interpretation of future differences
If the clean ten-repeat rerun changes generator rankings or numerical estimates, those new results become the PEERFIX-Core v1.0 derivation results. Historical five-repeat values remain an audit comparator, not a target to reproduce by force.

If the first five deterministic repeats reproduce the manuscript-facing values within a pre-specified tolerance, lineage equivalence is supported. If they do not, the discrepancy must be documented and traced rather than manually reconciled.

## Next gate
**Gate 0.2 — Pre-freeze protocol specification**

Create and review `PEERFIX_CORE_v1.0_PRE_FREEZE.yaml`, including dataset hash, folds/repeats, seed map, generators, hyperparameters, downstream models, TSTR/TRTR/Delta definitions, ICD reference effects, magnitude bands, lambda, DCR policy, eligibility gates, failure policy, and adapter boundaries.

No external confirmatory processing is authorised until Gate 0.2 is approved and the clean derivation rerun passes reproducibility checks.
