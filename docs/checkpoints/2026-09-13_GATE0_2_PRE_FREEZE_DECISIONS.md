# PEERFIX-Core v1.0 — Gate 0.2 Pre-Freeze Decision Record

Date: 2026-09-13  
Status: **PROTOCOL PROPOSED — NOT YET FROZEN**

Canonical candidate specification: `config/PEERFIX_CORE_v1.0_PRE_FREEZE.yaml`

## Why Gate 0.2 exists
Gate 0.1 showed that the late PEERFIX2 manuscript-facing results are scientifically interpretable but do not preserve a uniquely reconstructable execution lineage for the five-repeat utility table. At least two strict repeated-k-fold states existed, one with five and one with ten repeats. The correct response is therefore not to force reproduction of a preferred historical table, but to define a clean protocol before any new result is observed.

The objective of Gate 0.2 is to convert the accumulated methodological lessons into a pre-specified PEERFIX-Core candidate that can be implemented, smoke-tested and then rerun from the immutable derivation dataset.

## Decision matrix

| Item | Gate 0.2 decision | Scientific rationale | Historical compatibility |
|---|---|---|---|
| Derivation dataset | Keep the 20-run PEERFIX2 factorial dataset, SHA-256 fixed | It is the development dataset and is sufficiently structured to derive the Core | Full compatibility |
| Utility CV | 5 folds × 10 repeats as primary | Matches the stricter historical runbook and gives more split-level stability than five repeats | First five deterministic repeats retained as explicit comparator |
| Generator leakage | Refit generator inside every real-training fold | Required for valid TSTR on held-out real observations | Strengthens the late PEERFIX2 rule |
| Downstream-model selection | No data-dependent `m*` for primary inference | Selecting the model that maximizes TSTR on the same repeated CV is optimistic | Historical `m*` retained only as descriptive table |
| Primary downstream reference | Linear Regression | Low-variance, pre-declared reference aligned with the small designed experiment | LR was already part of all mature PEERFIX2 states |
| Secondary model panel | RF, GBR, MLP with fixed hyperparameters | Preserves nonlinear sensitivity without allowing post-result tuning | Compatible with late manuscript panel |
| Direct augmentation metric | Add real+synthetic training (`AUGTR`) as secondary | The scientific claim is augmentation/complementation, so a direct augmentation condition is informative | New secondary analysis; does not replace TSTR/TRTR |
| Utility uncertainty | Report repeat-level distribution; any t-based 95% interval labelled a repeated-CV variability interval, not a population CI | Repeated CV scores are not independent population samples | Corrects over-interpretation risk |
| Center-point condition grouping | Mandatory grouped-by-design-condition CV sensitivity | Tests whether results depend on splitting replicate runs of the same condition across folds | New robustness analysis |
| ICD reference truth | Primary set = confirmed KH2PO4 effect; expanded set adds the candidate urea × ammonium-sulfate interaction | The second effect was not independently confirmed and should not carry equal primary evidential status | Historical two-effect ICD retained as sensitivity |
| ICD detectability | Compute from matched-effective-n synthetic subsamples, not directly from n=140 | Prevents artificial significance caused only by synthetic sample-size inflation | Major methodological improvement |
| ICD magnitude | Anchor tolerance to the real coefficient uncertainty rather than fixed absolute bands | More defensible across scales and datasets than the heuristic 0.5/0.3/0.2 bands | Legacy magnitude bands retained for comparison only |
| ICD S/M/D | Use proportions across 1000 matched-n subsamples | Converts unstable one-shot binary decisions into auditable stability measures in [0,1] | New primary ICD-Core candidate |
| ICD penalty | Keep λ=0.10 primary, evaluate 0/0.05/0.10/0.20 sensitivity | Preserves continuity while exposing penalty dependence | Compatible with historical λ=0.10 |
| DCR | Diagnostic only; no primary threshold filtering, top-up or repulsion | DCR is not a privacy certificate; filtering plus repulsion changes the generated distribution and the historical implementation mixes diagnostic and generation roles | `fraction DCR<0.10` retained only as a historical comparator |
| Post-processing | Factor support/snap may use training-fold design support; target is not clipped to observed training range | Prevents held-out leakage and avoids truncating the response merely to mimic observed extrema | Tightens historical post-processing |
| Synthetic size | Keep n=140 for PEERFIX2 derivation; explicitly state that it is not optimal and adds no experimental evidence | Preserves derivation comparability without claiming a theoretical optimum | Full compatibility for derivation |
| Generator families | Gaussian Copula, CTGAN, TVAE, TabDDPM | These are the four established PEERFIX families | Full compatibility |
| External adaptation | Schema, units, grouping, constraints and reference relations may adapt; Core algorithms/thresholds may not | Separates transportability from retuning | Formalizes the planned Core + Adapter architecture |
| Failure handling | No silent proxy generator, no imputation of failed folds, no hidden dropping of failures | Essential for auditable reproducibility | Strengthens historical practice |

## Important methodological corrections introduced before freeze

### 1. Primary utility no longer depends on choosing the winning downstream model
The late manuscript chooses `m*` as the model with the highest mean TSTR and then reports TSTR, TRTR and Delta for that model. Although the same-model Delta rule is correct, using the same repeated-CV evidence to choose the model and summarize its performance can make the headline result optimistic.

Gate 0.2 therefore pre-declares Linear Regression as the primary reference model for PEERFIX2. RF, GBR and MLP remain fixed secondary models. A “best observed model” table may still be produced, but it is explicitly descriptive and cannot define the primary inferential conclusion.

### 2. Detectability in ICD is decoupled from the artificial synthetic sample size
The historical ICD asked whether an effect is significant in a regression fitted to the full synthetic dataset. With `n_synth=140` versus `n_real=20`, detectability can improve simply because standard errors shrink with the larger artificial sample, even though no new biological experiment occurred.

The candidate ICD-Core therefore repeatedly draws matched-effective-size subsamples of `n=20` from each synthetic realization. For each reference effect, the following quantities are computed across 1000 deterministic subsamples:

- `S`: proportion with the same coefficient sign as the real model;
- `M`: proportion whose coefficient lies inside the uncertainty band around the real coefficient;
- `D`: proportion with `p<0.05` at matched effective sample size;
- `R_spurious`: mean fraction of non-reference terms significant in synthetic but not in the real coded model.

The primary candidate remains `ICD = mean(S,M,D) - 0.10 * R_spurious`, but S/M/D are now stability proportions rather than one-shot binary outcomes.

### 3. The primary ICD reference set is narrowed to independently supported domain truth
The KH2PO4 main effect remains the primary confirmed reference relation. The urea × ammonium-sulfate interaction is retained in a secondary expanded reference set because it was borderline/candidate in the PEERFIX re-fit and was not independently established with the same strength.

This distinction prevents the Core from treating a result discovered during its own derivation as if it were equally strong external ground truth.

### 4. DCR is separated from the act of generating the synthetic dataset
The historical code computes DCR after scaling predictors on the real reference set and contains an optional threshold filter with synthetic top-up/repulsion. That procedure changes the synthetic sample after generation and its comments are not fully consistent with the actual StandardScaler implementation.

Gate 0.2 therefore makes DCR diagnostic only. The full ECDF and quantiles are retained, and `fraction DCR < 0.10` remains a historical comparison, but no PEERFIX-Core primary sample is filtered or repelled on that basis.

## What is still intentionally not frozen
Gate 0.2 is a specification candidate, not the final Core. Before freeze we still need to:

1. implement a minimal clean engine from the YAML rather than reuse a historically accreted orchestration script;
2. pin and smoke-test the computational environment and every generator dependency;
3. verify that deterministic seeds propagate through SDV, NumPy, Python and PyTorch;
4. generate a machine-readable per-fold execution manifest;
5. run unit tests on leakage, fold membership, model selection, ICD matched-n logic and failure handling;
6. perform the clean PEERFIX2 derivation rerun;
7. compare the first five deterministic repeats with the current five-repeat manuscript table without forcing agreement;
8. audit all new tables/figures back to raw machine-readable outputs.

## Gate 0.2 decision
**PASS as a pre-freeze candidate specification, subject to implementation/smoke testing.**

This is not yet `PEERFIX_CORE_v1.0_FROZEN.yaml`.

## Next authorized gate
**Gate 0.3 — Environment, engine implementation and smoke tests**

No external confirmatory dataset is authorized for processing at Gate 0.3. The only permitted execution data are the derivation dataset and purpose-built pseudodata/unit-test fixtures.
