# PEERFIX — Resume Point after Gate 0.3

Date: 2026-09-13  
State: **SAFE STOP / READY TO RESUME**

## Repository state
Repository:
`FGarcia9999/Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2`

Working branch:
`checkpoint/peerfix-core-v1-freeze-2026-09-13`

Current scientific protocol:
`config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV2.yaml`

Current protocol pointer:
`config/CURRENT_PEERFIX_CORE_PROTOCOL.md`

Qualified environment snapshot:
`environment/gate03_environment_freeze.txt`

Source-confirmed PEERFIX2 derivation dataset:
`data/derivation/peerfix2_historical_manuscript_dataset.csv`

Authorized dataset SHA-256:
`c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

Quarantined dataset remains prohibited:
`data/quarantine/cleanup_substituted_dataset_6161c35.csv`

## Gate 0.3 final status
**PASS.**

Final protocol-aligned CI evidence:
- workflow run: `34742575894`;
- tested commit: `4d30d5b93517a66784d8491a83e6d9acdda9b375`;
- Core contract stage: success;
- four-generator real fit/sample smoke stage: success;
- overall job: success.

The four executable generator families are integrated in the clean Core:
- Gaussian Copula;
- CTGAN;
- TVAE;
- PEERFIX small-n TabDDPM.

The Gate 0.3 methodological correction is already integrated: stochastic downstream-model seeds are invariant to generator identity for the same scenario/repeat/fold/model, so TRTR cannot be altered merely by changing the generator label.

## Exact point to resume
Resume with **Gate 0.4 — clean PEERFIX2 derivation rerun**. Do not begin external confirmatory execution yet.

The first pending technical item is the historical `sensitivity_1pct` scenario. The legacy scripts contain `apply_doe_based_noise(...)`; its semantics were located, but it has **not yet been migrated into the clean Core**. Before any scientific Gate 0.4 run, inspect that legacy function and reimplement only the scientifically defensible behavior under the REV2 rule: adapter-specific sensitivity, training-fold calibration only during utility validation, deterministic seed control, no held-out information, and no silent response clipping.

After that, build the Gate 0.4 clean derivation runner with fail-closed preflight checks for the authorized dataset hash and current protocol identity. The runner must execute the predeclared baseline and historical sensitivity without retuning; run the primary repeated 5-fold x 10-repeat row-level CV and mandatory grouped-condition robustness CV; evaluate TRTR/TSTR/AUGTR using the fixed downstream model panel; generate 10 full synthetic realizations per generator/scenario for ICD/fidelity/DCR analyses; and emit machine-readable fold manifests, repeat-level metrics, prediction hashes, synthetic hashes, warnings/exceptions and elapsed time.

Historical PEERFIX2 5x5 results are comparison evidence only. They must not be forced to match and must not be used to tune the new Core.

## Scientific stop rules carried forward
- No external confirmatory dataset may influence Core tuning or thresholds before Gate 0.5.
- No generator proxy substitution.
- No target clipping to the observed training range.
- DCR remains diagnostic only.
- Synthetic rows are not biological/experimental replicates.
- Failures are logged, not imputed or silently dropped.
- External adapters may map domain/schema/design structure, but may not change frozen Core logic after Gate 0.5.

## Next checkpoint target
When Gate 0.4 is complete, create a dedicated checkpoint containing:
- exact protocol hash;
- exact dataset hash;
- executable environment identity;
- complete run manifest;
- primary and grouped-CV repeat-level results;
- full-realization ICD/fidelity/DCR outputs;
- historical-comparison table;
- integrity audit showing no leakage and no silent missing folds.

Only after Gate 0.4 passes should Gate 0.5 reproducibility audit and final Core freeze begin.
