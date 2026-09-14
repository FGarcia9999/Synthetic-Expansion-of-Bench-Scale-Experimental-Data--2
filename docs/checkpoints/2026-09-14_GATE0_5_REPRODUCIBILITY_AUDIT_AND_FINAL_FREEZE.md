# Gate 0.5 — reproducibility audit and final PEERFIX-Core freeze

Date: 2026-09-14

## Inputs audited

- Gate 0.4 preflight run: `34891251335` — PASS.
- Gate 0.4 scientific run: `34893947717` — PASS.
- Scientific commit: `74b827768e0401de2aa24fb30bc69896dca6ae6b`.
- Protocol identity during Gate 0.4: `PEERFIX_CORE_v1.0_PRE_FREEZE_REV3`.
- Protocol SHA-256: `4ea74a46938f133db8e88ca2db446dc8d84f3815732709dbdb6c217dfa038e06`.
- Authorized derivation dataset SHA-256: `c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`.
- No external confirmatory dataset was used before freeze.

## Audit findings

### 1. Completeness — PASS

The scientific workflow executed every predeclared combination:

- utility: 4 generators × 2 scenarios × 2 CV geometries = 16 combinations;
- full realisations: 4 generators × 2 scenarios = 8 combinations;
- 10 repeats / 5 folds for each utility combination;
- 10 full synthetic realisations for each generator/scenario combination.

Both scientific jobs completed successfully and uploaded evidence artifacts.

### 2. Canonical provenance / hashes — PASS

The provenance-only repair was exercised in the scientific workflow before artifact upload.

`gate04_finalize_provenance.py` is fail-closed and requires:

- exactly 16 utility completion directories;
- exactly 600 prediction groups per utility combination;
- exactly 8 full-realisation completion directories;
- exactly 10 full realisations per generator/scenario;
- exactly 10 unique synthetic hashes per generator/scenario;
- round-trip-verifiable persisted dataframe hashes.

The finalizer returned PASS for all 16 utility entries and all 8 full-realisation entries. Therefore the prior hash/persistence mismatch is resolved for this accepted run.

### 3. Seed uniqueness / Gaussian Copula — PASS

The full-realisation provenance finalizer requires 10 unique synthetic hashes in every generator/scenario block. The accepted run passed this check for all eight blocks, including `gaussian_copula / baseline_0pct`; consequently the earlier one-hash-across-ten-seeds defect is not present in the accepted run.

### 4. Leakage controls — PASS

The accepted protocol fixes generator fitting, postprocessing calibration, and sensitivity calibration to real training-fold information during utility validation; held-out real rows are never authorized for generator fitting, tuning, or selection. Structural CV keeps exact-condition groups, including center-point replicates, together. The fail-closed preflight and the same runner previously qualified for these contracts both passed at the accepted commit.

### 5. TRTR comparability — PASS

The frozen seed contract deliberately excludes generator identity from downstream-model seed derivation. Therefore, for a fixed scenario/repeat/fold/model, TRTR stochastic initialization is generator-invariant. Gate 0.4 used this accepted REV2/REV3 contract unchanged.

### 6. TabDDPM conformance — PASS

The accepted preflight passed the explicit TabDDPM conformance contract. The scientific run executed both TabDDPM scenarios under both utility CV geometries and both full-realisation scenarios without fallback/proxy substitution.

### 7. Protocol adherence — PASS

The accepted scientific jobs reported the authorized derivation dataset, expected protocol label/hash, fixed model panel, fixed generator set, fixed CV geometries, fixed seed policy, matched-effective-n primary ICD, historical full-n ICD only as comparability sensitivity, and DCR only as a proximity diagnostic.

## Gate decision

**Gate 0.4: PASS.**

**Gate 0.5 reproducibility audit: PASS.**

The prior provenance blocker is resolved in the accepted Gate 0.4 run. No remaining blocking discrepancy was identified in the predeclared audit scope.

## Final freeze

PEERFIX-Core v1.0 is frozen in:

`config/PEERFIX_CORE_v1.0_FROZEN.yaml`

Freeze branch:

`freeze/peerfix-core-v1.0-2026-09-14`

The final freeze prohibits outcome-driven changes to Core algorithms, generator families/hyperparameters, seed policy, leakage rules, primary metric definitions, ICD component logic, ICD lambda, and DCR role. External datasets may now be evaluated only through predeclared adapters; external outcomes may not be used to retune the frozen Core.

## Next scientific phase

External confirmatory validation may begin only from this frozen Core snapshot and under an adapter declared before viewing confirmatory outcomes. The Peterson dataset and any dataset supplied by Lívia therefore remain external confirmation sources, not derivation/tuning data.
