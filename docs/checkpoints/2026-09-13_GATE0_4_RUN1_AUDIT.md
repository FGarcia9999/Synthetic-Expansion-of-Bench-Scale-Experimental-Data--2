# Gate 0.4 — Scientific rerun 1 audit

Date: 2026-09-13
Branch: `resume/gate0.4-clean-derivation-2026-09-13`
Scientific workflow run: `34767064409`
Execution commit: `fcab745009c89df8e93b4b5a9cb21b442170115a`
Protocol: `PEERFIX_CORE_v1.0_PRE_FREEZE_REV3`
Dataset SHA-256: `c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

## Workflow status
Both scientific jobs completed successfully at the workflow level:
- utility: SUCCESS;
- full-realisations: SUCCESS.

Artifacts downloaded and independently SHA-256 checked:
- utility artifact digest: `a5424ebebc9f9982ebaec7eb94293881409e40060571afbada02073f6fbe5d0f`;
- full-realisations artifact digest: `1c831764a172ff04b59b5816d2b9bc28140e7095d6eeaa147db35629a0a95896`.

## Completeness and leakage audit
The run produced all predeclared combinations:
- utility: 4 generators x 2 scenarios x 2 CV geometries = 16 combinations;
- each utility combination: 50 folds, 40 repeat/model rows, 600 prediction-manifest rows and 2400 held-out predictions;
- full realisations: 4 generators x 2 scenarios = 8 combinations;
- each full-realisation combination: 10 realisations, 140 synthetic rows per realisation, matched-n ICD, legacy ICD, fidelity/DOE and full DCR outputs.

Programmatic checks confirmed:
- all completion records are scientific PASS records;
- dataset and protocol hashes are consistent across outputs;
- no fold-level exceptions were silently dropped;
- train/test row sets are disjoint and complete;
- every real row is held out exactly once per repeat;
- grouped-condition CV keeps exact-factor groups disjoint between train and test;
- the same splits are used across generator comparisons;
- TRTR predictions are exactly identical across generators for the same scenario/geometry/repeat/fold/model, confirming downstream seed comparability and absence of generator contamination of the real-only baseline;
- all ten generator seeds are distinct in every full-realisation block.

## Blocking finding — Gaussian Copula baseline realisations are not independent
Despite ten distinct `generator_seed` values, the ten Gaussian Copula baseline realisations have the **same synthetic-data hash**:

- expected: 10 distinct synthetic realisations;
- observed: 1 distinct synthetic hash out of 10.

The 1% sensitivity scenario produces ten distinct hashes only because the post-generation response jitter uses a realisation-specific RNG stream. Therefore that scenario does not repair the missing Gaussian-Copula generator-level stochastic variation.

This is a blocking implementation defect for the claim of ten independent synthetic realisations. Gate 0.4 run 1 is consequently **not eligible for final PASS**, despite the GitHub Actions jobs themselves completing successfully.

## Root cause
The clean Core helper `_try_set_model_seed` attempts to seed the fitted SDV model directly. In SDV single-table synthesizers, however, sampling checks the synthesizer-level `_random_state_set` flag. If it remains false, SDV resets the fitted model to its built-in fixed sampling seed (`FIXED_RNG_SEED = 73251`) before sampling.

The correct version-qualified SDV hook is `synthesizer._set_random_state(seed)`, which both forwards the random state to the underlying model and marks `_random_state_set = True`.

This explains the observed pattern:
- Gaussian Copula fit is effectively deterministic on the same full derivation data and sampling was reset to the same SDV fixed seed, yielding identical baseline realisations;
- CTGAN and TVAE still varied because their fitted neural models differed with training seed even though the sampling-state binding was not correctly registered at the synthesizer level.

## Required corrective action
1. Repair the SDV random-state binding to use the synthesizer-level hook in the frozen SDV environment.
2. Add an explicit regression test requiring:
   - same Gaussian-Copula seed -> identical synthetic output;
   - different Gaussian-Copula seeds -> different synthetic output.
3. Re-run Gate 0.4 preflight.
4. Re-run the **entire** scientific Gate 0.4 matrix, not only Gaussian Copula, because the seed-binding implementation is shared by Gaussian Copula, CTGAN and TVAE.
5. Re-audit the replacement artifacts before Gate 0.5.

## Decision
**Gate 0.4 run 1: CONDITIONAL FAIL — implementation/RNG blocker.**

No external confirmatory dataset is authorized and Gate 0.5 must not begin until a corrected complete Gate 0.4 rerun passes the reproducibility audit.
