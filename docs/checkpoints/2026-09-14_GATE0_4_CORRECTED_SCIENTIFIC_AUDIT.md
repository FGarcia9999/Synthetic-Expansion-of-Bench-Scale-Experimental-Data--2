# PEERFIX — Gate 0.4 corrected scientific rerun audit

Date: 2026-09-14
Branch: `resume/gate0.4-clean-derivation-2026-09-13`
Scientific execution commit: `91e2ed4c47649ec75c74cbfd9377e503850cbe21`
GitHub Actions run: `34791248850`
Protocol label: `PEERFIX_CORE_v1.0_PRE_FREEZE_REV3`
Protocol SHA-256: `4ea74a46938f133db8e88ca2db446dc8d84f3815732709dbdb6c217dfa038e06`
Derivation dataset SHA-256: `c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

## 1. Workflow completion

Both scientific jobs completed successfully:
- utility: PASS
- full-realisations: PASS

Artifacts:
- `gate04-utility-91e2ed4c47649ec75c74cbfd9377e503850cbe21`
  - GitHub artifact digest: `sha256:102c936252fc05f800833129deb5fa578d9f63311c8761aab8eff4501be5567b`
- `gate04-full-realisations-91e2ed4c47649ec75c74cbfd9377e503850cbe21`
  - GitHub artifact digest: `sha256:f7cee2b3d78d4854067b27c6d2d3c3cf15e64fcb480fa5eccdc1e3c014fd8a7e`

## 2. Integrity audit

Utility artifact contains all 16 predeclared combinations:
4 generators × 2 scenarios × 2 CV geometries.

For each combination:
- 50 folds observed = 5 folds × 10 repeats;
- 40 repeat/model rows observed = 10 repeats × 4 downstream models;
- 600 prediction-manifest rows observed = 50 folds × 4 models × 3 regimes;
- no train/test row overlap;
- grouped-condition CV has no train/test condition overlap;
- no generator exceptions;
- all 50 generator seeds and synthetic hashes are distinct within each utility combination.

TRTR invariance audit:
- for a fixed scenario/geometry/repeat/model, TRTR metrics are exactly invariant across the four generator identities;
- TRTR held-out prediction hashes are likewise identical across generators.

Full-realisation artifact contains all 8 predeclared combinations:
4 generators × 2 scenarios, each with 10/10 completed realisations.

Seed regression blocker from Run 1 is resolved:
- Gaussian Copula baseline: 10 unique generator seeds and 10 unique synthetic hashes;
- every other generator/scenario combination: 10 unique seeds and 10 unique synthetic hashes.

## 3. Primary utility results — Linear Regression reference model

Mean R² across 10 repeats. Negative absolute R² means the held-out predictive performance is worse than predicting the held-out mean; positive Delta alone must therefore not be interpreted as absolute predictive success.

### Primary row-wise repeated CV

| Generator | Scenario | TRTR R² | TSTR R² | Δ=TSTR−TRTR | AUGTR R² | Δaug |
|---|---|---:|---:|---:|---:|---:|
| TVAE | baseline | -0.505 | -0.187 | +0.319 | -0.187 | +0.319 |
| Gaussian Copula | baseline | -0.505 | -0.439 | +0.066 | -0.405 | +0.101 |
| CTGAN | baseline | -0.505 | -0.722 | -0.216 | -0.573 | -0.068 |
| TabDDPM | baseline | -0.505 | -10728.739 | -10728.234 | -9974.301 | -9973.796 |
| TVAE | sensitivity 1% | -0.505 | -0.186 | +0.320 | -0.187 | +0.319 |
| CTGAN | sensitivity 1% | -0.505 | -0.408 | +0.097 | -0.289 | +0.216 |
| Gaussian Copula | sensitivity 1% | -0.505 | -0.450 | +0.056 | -0.418 | +0.087 |
| TabDDPM | sensitivity 1% | -0.505 | -22730.101 | -22729.595 | -26732.200 | -26731.695 |

### Structural grouped-condition CV

| Generator | Scenario | TRTR R² | TSTR R² | Δ=TSTR−TRTR | AUGTR R² | Δaug |
|---|---|---:|---:|---:|---:|---:|
| TVAE | baseline | -0.375 | -0.136 | +0.240 | -0.141 | +0.234 |
| Gaussian Copula | baseline | -0.375 | -0.355 | +0.021 | -0.309 | +0.067 |
| CTGAN | baseline | -0.375 | -0.754 | -0.379 | -0.544 | -0.168 |
| TabDDPM | baseline | -0.375 | -30782.441 | -30782.066 | -28437.412 | -28437.037 |
| TVAE | sensitivity 1% | -0.375 | -0.060 | +0.315 | -0.077 | +0.298 |
| Gaussian Copula | sensitivity 1% | -0.375 | -0.403 | -0.028 | -0.331 | +0.044 |
| CTGAN | sensitivity 1% | -0.375 | -0.603 | -0.228 | -0.477 | -0.102 |
| TabDDPM | sensitivity 1% | -0.375 | -37350.917 | -37350.541 | -33125.308 | -33124.933 |

Interpretation: TVAE is consistently the least-bad generator for predictive transport in this very small derivation dataset and improves relative to the real-only LR baseline, but its absolute TSTR R² remains below zero. Therefore the clean run does **not** support a claim of strong absolute predictive utility from synthetic-only training.

## 4. ICD matched-effective-n primary results

Primary reference set = confirmed `kh2po4_pv` relation only; n matched to 20, 1000 subsamples per realisation, lambda=0.10.

Mean ± SD across 10 full realisations:
- Gaussian Copula baseline: `0.612 ± 0.048`; sensitivity: `0.615 ± 0.070`
- TVAE baseline: `0.467 ± 0.050`; sensitivity: `0.460 ± 0.095`
- TabDDPM baseline: `0.365 ± 0.153`; sensitivity: `0.483 ± 0.098`
- CTGAN baseline: `0.291 ± 0.029`; sensitivity: `0.306 ± 0.042`

The TabDDPM composite ICD must not be interpreted in isolation: its magnitude component is near zero while its generated response distribution is unstable.

## 5. Fidelity / structural diagnostics

Baseline mean values across 10 full realisations:

| Generator | KS | Wasserstein | corr-of-corr | factorial-cell coverage | off-design fraction |
|---|---:|---:|---:|---:|---:|
| Gaussian Copula | 0.234 | 1.084 | 0.831 | 0.900 | 0.570 |
| TVAE | 0.156 | 0.793 | 0.564 | 0.541 | 0.735 |
| CTGAN | 0.269 | 2.229 | 0.052 | 0.618 | 0.776 |
| TabDDPM | 0.616 | 201.162 | 0.189 | 0.706 | 0.039 |

The synthetic response distributions pooled across the 10 baseline realisations show:
- real response range: 42.22–53.57 mN/m;
- Gaussian Copula: 40.25–53.57; 4.0% outside the real range;
- TVAE: 38.31–57.61; 4.1% outside;
- CTGAN: 35.23–60.08; 32.4% outside;
- TabDDPM: -1748.50–1544.93; 95.7% outside.

No target clipping was applied, as predeclared.

## 6. Gate decision

### Corrected seed-binding issue
PASS. The Run-1 Gaussian Copula repeated-output defect is fixed and verified.

### Gate 0.4 overall
**BLOCKED / CONDITIONAL FAIL for final freeze.**

Reason: the audit found a protocol/implementation discrepancy in the clean TabDDPM implementation. REV2 predeclares `timestep_loss_weighting: true`, but `peerfix_core/tabddpm.py` currently trains with an unweighted MSE. The historical improved implementation explicitly applied timestep weighting. The historical implementation also used posterior diffusion variance and discrete-aware bootstrap jitter; the clean implementation differs in these details. Historical percentile clipping is *not* to be reintroduced automatically because the current Core explicitly prohibits clipping the response to the observed range.

Because the TabDDPM implementation does not yet faithfully execute the predeclared algorithmic contract, the catastrophic TabDDPM output cannot be accepted as the final scientific result without a corrective implementation audit and rerun.

## 7. Next allowed action

Do not start Gate 0.5 yet.

Perform a non-outcome-tuned TabDDPM conformance patch restricted to predeclared/historical algorithm semantics:
1. implement the already predeclared timestep loss weighting;
2. align reverse-process variance with the historical posterior-variance implementation;
3. restore discrete-aware bootstrap jitter for DOE factor columns while retaining target jitter behavior;
4. retain the current no-target-clipping rule;
5. add regression/unit tests for these semantics;
6. rerun Gate 0.4 in full and re-audit all artifacts.

No external confirmatory dataset may be used during this correction.
