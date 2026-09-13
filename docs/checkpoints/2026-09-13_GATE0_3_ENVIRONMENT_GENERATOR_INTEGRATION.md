# PEERFIX-Core v1.0 — Gate 0.3 Environment and Generator Integration

Date: 2026-09-13  
Status: **PASS — CLEAN CORE INTEGRATION QUALIFIED**

## Purpose
Gate 0.3 converts the scientific contract from Gate 0.2C into a clean executable Core before any derivation rerun. No external validation dataset was used here.

## Repository integration completed
A clean `peerfix_core/` package is now the execution target. Historical monolithic scripts remain historical evidence and are not imported by the new Core.

Qualified clean primitives:
- deterministic SHA-256 seed derivation;
- exact SHA-256 guard for the source-confirmed derivation CSV;
- repeated 5-fold row-level CV;
- repeated grouped-condition CV keeping exact factor tuples intact;
- leakage-free TRTR/TSTR/AUGTR fold-refit utility evaluation;
- downstream stochastic seed invariant across generators for the same scenario/repeat/fold/model;
- matched-effective-n ICD candidate;
- DCR as a diagnostic only.

Generator integration qualified in this gate:
- `gaussian_copula` — SDV GaussianCopulaSynthesizer;
- `ctgan` — SDV CTGANSynthesizer;
- `tvae` — SDV TVAESynthesizer;
- `tabddpm` — clean PyTorch `PEERFIX_small_n_TabDDPM` implementation.

The generator API receives only the real training fold, requested synthetic size and deterministic generator seed. Declared DOE factors are snapped back to the adapter-declared support after generation. The response is not clipped to the observed training range.

## Important Gate 0.3 methodological correction
During contract review, the downstream-model seed originally included `generator_name`. That would allow RF/GBR/MLP initialization to differ across generator comparisons and therefore could change TRTR even though the real training/test rows were identical.

This was corrected before Gate 0.3 closure. Downstream seeds now depend on scenario/repeat/fold/model but **not** generator identity. An explicit Random-Forest contract test verifies exact TRTR equality across two different generator names.

The change is versioned scientifically in:

`config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV2.yaml`

REV2 is now the current protocol pointer for Gate 0.4 and later work.

## Environment
Successful CI environment:
- Ubuntu 24.04.5 LTS;
- Python 3.12.14;
- NumPy 2.3.5;
- Pandas 2.3.3;
- SciPy 1.17.1;
- scikit-learn 1.9.1;
- statsmodels 0.14.6;
- SDV 1.38.2;
- CTGAN 0.12.1;
- PyTorch 2.14.0;
- pytest 8.4.2.

The full transitive `pip freeze` from the successful qualification environment is preserved at:

`environment/gate03_environment_freeze.txt`

This is the Gate 0.3 qualified environment snapshot. The final release lock remains a Gate 0.5 artifact.

## TabDDPM implementation boundary
The clean TabDDPM is a real diffusion generator, not a proxy substitution. It implements:
- robust + standard scaling;
- light bootstrap augmentation;
- regularized residual denoising MLP;
- cosine diffusion schedule;
- AdamW with weight decay;
- gradient clipping;
- reduce-on-plateau scheduling;
- early stopping;
- deterministic seed controls.

Scientific settings remain those declared in the current pre-freeze protocol: 150 epochs, 100 timesteps, hidden dimension 128, two layers, dropout 0.15, LR 5e-4, weight decay 0.01, gradient clip 0.5. Smoke mode reduces only epochs/timesteps for integration testing and is explicitly non-scientific.

## CI evidence
Workflow:
`.github/workflows/gate03-smoke.yml`

Initial infrastructure attempt `34742162684` failed before tests because setup-python cache discovery expected `requirements.txt`/`pyproject.toml`. The workflow was corrected with an explicit `cache-dependency-path`; no scientific result was affected.

Successful qualification sequence:
- run `34742186473`: environment installed, original Core contract suite passed, all four real generator fit/sample smoke calls passed;
- run `34742260429`: source-confirmed derivation-data SHA guard included and passed;
- run `34742387739`, commit `2539309303e8be3ab758d8b4d95d964a4a80d070`: **final Gate 0.3 functional qualification PASS** after downstream-seed deconfounding;
- run `34742575894`, commit `4d30d5b93517a66784d8491a83e6d9acdda9b375`: **final protocol-aligned CI PASS**, after the workflow trigger was updated to follow `PEERFIX_CORE_v1.0_PRE_FREEZE_REV2.yaml`.

Final protocol-aligned run results:
- Core contract: **success**;
- four-generator integration smoke: **success**;
- complete job conclusion: **success**.

The generator smoke emitted only version/deprecation warnings from pinned third-party SDV/CTGAN APIs (`SingleTableMetadata` future deprecation and `cuda` parameter deprecation). No fit/sample failure occurred. These warnings are non-blocking under the pinned Gate 0.3 environment and will be re-evaluated before the final Gate 0.5 release lock.

## Gate decision
**PASS.**

Gate 0.4 — clean derivation rerun — is authorized under `PEERFIX_CORE_v1.0_PRE_FREEZE_REV2.yaml`.

External confirmatory datasets remain prohibited until Gate 0.5 final freeze.

## Gate 0.4 requirements
The clean derivation runner must validate the exact dataset hash and current protocol hash before work begins; refuse the quarantined dataset; execute only predeclared scenarios/generators/CV geometries; preserve fold-level seeds, row/group membership, hashes, elapsed time, warnings and exceptions; generate machine-readable repeat-level outputs; and never tune against external datasets.
