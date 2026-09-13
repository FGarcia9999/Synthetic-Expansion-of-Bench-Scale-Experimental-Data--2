# PEERFIX-Core v1.0 — Gate 0.3 Environment and Generator Integration

Date: 2026-09-13  
Status: **IN PROGRESS — CI SMOKE PENDING**

## Purpose
Gate 0.3 converts the scientific contract from Gate 0.2C into a clean executable Core before any derivation rerun. No external validation dataset is used here.

## Repository integration completed
A clean `peerfix_core/` package is now the execution target. Historical monolithic scripts remain historical evidence and are not imported by the new Core.

Existing clean primitives:
- deterministic SHA-256 seed derivation;
- repeated 5-fold row-level CV;
- repeated grouped-condition CV keeping exact factor tuples intact;
- leakage-free TRTR/TSTR/AUGTR fold-refit utility evaluation;
- matched-effective-n ICD candidate;
- DCR as a diagnostic only.

Generator integration added in this gate:
- `gaussian_copula` — SDV GaussianCopulaSynthesizer;
- `ctgan` — SDV CTGANSynthesizer;
- `tvae` — SDV TVAESynthesizer;
- `tabddpm` — clean PyTorch `PEERFIX_small_n_TabDDPM` implementation.

The generator API receives only the real training fold, requested synthetic size and deterministic seed. Declared DOE factors are snapped back to the adapter-declared support after generation. The response is not clipped to the observed training range.

## Environment
Gate 0.3 CI uses Python 3.12 and `requirements-gate03.txt`.

Primary execution pins:
- SDV 1.38.2;
- scikit-learn 1.9.1;
- statsmodels 0.14.6;
- PyTorch 2.14.0;
- NumPy/Pandas/SciPy constrained to compatible version ranges pending the final Gate 0.5 lock file.

The final exact transitive environment lock is not considered frozen until the successful CI environment is captured and Gate 0.5 is reached.

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

Scientific protocol settings remain those declared in `PEERFIX_CORE_v1.0_PRE_FREEZE_REV1.yaml` (150 epochs, 100 timesteps, hidden dimension 128, two layers, dropout 0.15, LR 5e-4, weight decay 0.01, clip 0.5). Smoke mode reduces only epochs and timesteps for integration testing and is explicitly non-scientific.

## CI contract
Workflow: `.github/workflows/gate03-smoke.yml`

Tests:
1. Core contract tests: seed determinism, complete repeated-CV coverage, no grouped-condition leakage, fold-safe utility, matched-n ICD execution, DCR diagnostics.
2. Four-generator smoke: actual fit/sample call for all four declared generators on the source-confirmed PEERFIX2 derivation table, with factor-support and finite-output checks.

## First CI attempt
Run `34742162684` failed before dependency installation because `actions/setup-python` pip caching searched only for `requirements.txt`/`pyproject.toml`. No scientific or code test ran. The workflow was corrected by explicitly setting `cache-dependency-path: requirements-gate03.txt`.

This infrastructure-only failure is not a Gate 0.3 scientific failure.

## Gate decision
**Pending the corrected CI run.**

Gate 0.4 remains blocked until:
- the four real generator implementations import, fit and sample successfully in the pinned environment;
- Core contract tests pass;
- any compatibility defect is fixed and rerun;
- the successful environment is recorded.
