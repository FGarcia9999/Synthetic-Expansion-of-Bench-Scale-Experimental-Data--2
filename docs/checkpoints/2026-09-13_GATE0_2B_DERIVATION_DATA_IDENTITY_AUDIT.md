# PEERFIX-Core v1.0 — Gate 0.2B Derivation Data Identity Audit

Date: 2026-09-13  
Status: **BLOCKING DATA-IDENTITY DISCREPANCY IDENTIFIED — MANUSCRIPT-LINEAGE DATASET RECOVERED**

## Purpose
During implementation of Gate 0.3 contract tests, the derivation dataset on the clean `cce-v26-zenodo-metadata` branch was checked against the factorial coefficients reported in the PEERFIX2 manuscript and against the raw ICD audit outputs preserved in repository history. This exposed a more serious lineage problem than the previously known loss of intermediate execution files: the cleanup branch contains a different 20-row response table from the one used to produce the manuscript and historical ICD results.

This report freezes the evidence before any new generator execution.

## 1. Two distinct 20-row datasets exist in PEERFIX2 history

### Dataset A — manuscript-lineage derivation dataset
Recovered from `data/dados.csv` at historical commit:

`4ac9fdf8585a4592d7214aa99df1b5fffc07fa1d`

and confirmed unchanged in the parent of the cleanup commit:

`f96bc89f0688b0db1332322585a95129bd4337b2`

A protected copy has now been created at:

`data/derivation/peerfix2_historical_manuscript_dataset.csv`

SHA-256 of the exact UTF-8 CSV bytes, including final newline:

`c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

Center-point responses are `49.44, 44.26, 47.75, 49.21` mN/m.

### Dataset B — dataset introduced by clean-release cleanup
The cleanup branch `cce-v26-zenodo-metadata` contains a different `data/dados.csv`, introduced at commit:

`6161c35bfe18d17d87b2b23750334e13b44749e8`

A verbatim quarantine copy has been created at:

`data/quarantine/cleanup_substituted_dataset_6161c35.csv`

SHA-256 of the exact UTF-8 CSV bytes, including final newline:

`d7420eaa5d1c45f1287e12af5737893b244a6302beecab0da35a2b464d040001`

Center-point responses are `48.09, 44.79, 48.35, 43.70` mN/m.

Dataset B must not be used for the PEERFIX-Core derivation rerun unless its experimental provenance is independently established and a separate scientific rationale is provided. It is not the dataset that generated the current manuscript's domain-effect results.

## 2. The cleanup commit itself substituted the data
Git history establishes the transition directly. The parent `f96bc89...` contains Dataset A. The cleanup commit `6161c35...`, whose message is `Clean branch to PEERFIX2 CCE release metadata and final summary outputs`, changes the 20 rows in `data/dados.csv` to Dataset B while also deleting historical material.

Therefore this is not merely a filename collision discovered after the fact. Dataset substitution occurred during the release-cleanup operation.

The correct audit treatment is preservation, not silent overwrite. Dataset B is therefore retained in quarantine, while Dataset A is preserved under an explicit derivation-lineage name.

## 3. Factorial-model fingerprint proves which dataset underlies the manuscript
Both datasets were fit with the PEERFIX2 coded model used by the ICD audit:

- four main effects;
- all six two-way interactions;
- real factor levels coded as `-1/0/+1`;
- ordinary least squares on surface tension.

### Dataset A fingerprint

| Term | coefficient | p value |
|---|---:|---:|
| KH2PO4 main effect | -1.916875 | 0.0301776 |
| Urea × ammonium sulfate | -1.885625 | 0.0323252 |

These values exactly match the real-effect values embedded in the historical PEERFIX2 ICD effect files and the values described in the mature manuscript.

### Dataset B fingerprint

| Term | coefficient | p value |
|---|---:|---:|
| Seawater main effect | +1.775000 | 0.0115271 |
| KH2PO4 main effect | -1.595000 | 0.0193821 |
| Urea × ammonium sulfate | +0.515000 | 0.382955 |
| Urea × KH2PO4 | -1.595000 | 0.0193821 |

Dataset B therefore produces a materially different scientific structure. In particular, it reverses the sign and removes the near-threshold behavior of the urea × ammonium-sulfate interaction, while adding other significant terms. It cannot have generated the manuscript's reported ICD reference coefficients.

## 4. Manuscript and raw-output consistency
The mature manuscript explicitly states that, for surface tension, the independently supported primary relation is the negative KH2PO4 main effect and that the negative urea × ammonium-sulfate interaction is only a candidate secondary effect from the PEERFIX refit. The historical raw ICD output records the corresponding real coefficients and p values as approximately `-1.916875 / 0.03018` and `-1.885625 / 0.03233`.

Those values are reproduced exactly by Dataset A and not by Dataset B.

This provides a strong internal lineage fingerprint even before the original experimental publication/thesis table is fully reconciled.

## 5. What is known and what remains unresolved
### Established
- Dataset A is the dataset used by the PEERFIX2 manuscript/ICD lineage.
- Dataset B was introduced during repository cleanup.
- Dataset A and Dataset B are scientifically non-equivalent.
- Any Core rerun intended to reproduce or revise PEERFIX2 must start from Dataset A, not Dataset B.

### Not yet established
- The exact original public table, page, supplement or laboratory export from which Dataset A was transcribed has not yet been uniquely identified in the currently audited source materials.
- The provenance and intended identity of Dataset B remain unresolved.
- Therefore Dataset A is **lineage-confirmed but source-confirmation-pending**.

## 6. Gate decision
**FAIL** for derivation-data source traceability as required for the final Core freeze.

**PASS** for recovery of the correct manuscript-lineage computational dataset.

The derivation rerun remains blocked until the source identity/provenance record is reconciled sufficiently for the intended publication claims.

## 7. Immediate protocol correction
The pre-freeze configuration must no longer identify `data/dados.csv` with SHA-256 `d7420eaa...` as the derivation dataset.

Until source reconciliation is complete, the candidate derivation input is:

`data/derivation/peerfix2_historical_manuscript_dataset.csv`

SHA-256:

`c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

with status:

`lineage_confirmed_source_confirmation_pending`

No generative derivation run is authorized while this status remains unresolved.

## 8. Consequence for previous Gate 0.1 / Gate 0.2 records
Gate 0.1 remains valid in its conclusion that historical execution lineage was incomplete, but its referenced derivation-file hash must be superseded by this Gate 0.2B audit.

Gate 0.2 methodological decisions remain candidates and are not invalidated by the data substitution. However, the provenance block in `PEERFIX_CORE_v1.0_PRE_FREEZE.yaml` must be corrected and a new blocking source-confirmation gate inserted before the clean derivation rerun.

## Next authorized work
1. reconcile Dataset A against the original published/thesis/table source and document row-level provenance;
2. identify, if possible, the source of Dataset B without using it to tune the Core;
3. keep implementing and testing generic Core code only on pseudodata while source reconciliation is pending;
4. do not execute Gaussian Copula, CTGAN, TVAE or TabDDPM on the real derivation dataset yet.
