# PEERFIX Gate 0.4 — final provenance-fixed scientific audit

Date: 2026-09-15
Branch: `resume/gate0.4-clean-derivation-2026-09-13`
Scientific run: `34893947717`
Scientific commit: `74b827768e0401de2aa24fb30bc69896dca6ae6b`
Protocol: `PEERFIX_CORE_v1.0_PRE_FREEZE_REV3`
Protocol SHA-256: `4ea74a46938f133db8e88ca2db446dc8d84f3815732709dbdb6c217dfa038e06`
Derivation dataset SHA-256: `c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

## Final decision

**Gate 0.4: PASS.**

The final provenance-fixed scientific run completed successfully for both jobs (`utility` and `full-realisations`) and passed the canonical provenance finalizer before artifact upload. No scientific tuning or external confirmatory execution occurred.

Gate 0.5 is therefore authorized.

## Evidence artifacts

- Utility artifact: `gate04-utility-74b827768e0401de2aa24fb30bc69896dca6ae6b`
  - GitHub artifact id: `10370239011`
  - artifact digest: `sha256:09913fb3067aa792b537041c57c939fe53c34889f195e22392fdfeb0ec6d6492`
- Full-realisations artifact: `gate04-full-realisations-74b827768e0401de2aa24fb30bc69896dca6ae6b`
  - GitHub artifact id: `10369160706`
  - artifact digest: `sha256:103fe5da868e341620d715dcaa80b591ed121b0c536de50584c0393d558cb342`

Both `provenance_roundtrip_report.json` files report `PASS`.

## Integrity audit

The downloaded final artifacts were independently audited after workflow completion.

Passed checks:

- all 4 generators × 2 scenarios × 2 CV geometries are present for utility;
- each utility combination contains exactly 50 folds (5 folds × 10 repeats), 40 repeat/model rows (10 repeats × 4 downstream models), and 600 prediction-manifest groups;
- all 4 generators × 2 scenarios contain 10 full synthetic realisations each;
- no `failure.json` is present;
- all completion manifests report `PASS`;
- derivation dataset and protocol hashes are uniform across the evidence;
- row train/test sets are disjoint in every fold;
- grouped-condition train/test condition sets are disjoint in every grouped fold;
- TRTR metrics are exactly generator-invariant for identical scenario/geometry/repeat/model, including stochastic downstream models;
- every generator/scenario has 10 distinct generator seeds and 10 distinct synthetic hashes;
- Gaussian Copula baseline specifically has 10/10 unique synthetic realisations;
- canonical round-trip provenance passes for all persisted synthetic CSVs and held-out prediction evidence using pandas `float_precision="round_trip"` plus the PEERFIX canonical CSV representation;
- post-scientific branch changes before this audit are documentation-only (Farias contact and Peterson/C. mogii provenance audit); no Core/config/test/runner file changed after scientific commit `74b8277...`.

## Final derivation findings

Primary downstream reference = linear regression.

### Row repeated CV (mean R² across 10 repeats)

| Scenario | Generator | TRTR | TSTR | Δ=TSTR−TRTR | AUGTR |
|---|---|---:|---:|---:|---:|
| baseline | TVAE | -0.5054 | **-0.1868** | **+0.3186** | -0.1869 |
| baseline | Gaussian Copula | -0.5054 | -0.4391 | +0.0664 | -0.4048 |
| baseline | CTGAN | -0.5054 | -0.7216 | -0.2162 | -0.5732 |
| baseline | TabDDPM | -0.5054 | -950.8094 | -950.3040 | -636.4333 |
| sensitivity 1% | TVAE | -0.5054 | **-0.1855** | **+0.3199** | -0.1868 |
| sensitivity 1% | Gaussian Copula | -0.5054 | -0.4499 | +0.0555 | -0.4182 |
| sensitivity 1% | CTGAN | -0.5054 | -0.4082 | +0.0972 | -0.2891 |
| sensitivity 1% | TabDDPM | -0.5054 | -482.6893 | -482.1838 | -508.8430 |

### Grouped-condition structural CV (mean R² across 10 repeats)

| Scenario | Generator | TRTR | TSTR | Δ=TSTR−TRTR | AUGTR |
|---|---|---:|---:|---:|---:|
| baseline | TVAE | -0.3751 | **-0.1356** | **+0.2395** | -0.1414 |
| baseline | Gaussian Copula | -0.3751 | -0.3546 | +0.0205 | -0.3086 |
| baseline | CTGAN | -0.3751 | -0.7544 | -0.3793 | -0.5435 |
| baseline | TabDDPM | -0.3751 | -1670.3169 | -1669.9418 | -1296.5541 |
| sensitivity 1% | TVAE | -0.3751 | **-0.0601** | **+0.3150** | -0.0774 |
| sensitivity 1% | Gaussian Copula | -0.3751 | -0.4028 | -0.0276 | -0.3315 |
| sensitivity 1% | CTGAN | -0.3751 | -0.6030 | -0.2279 | -0.4775 |
| sensitivity 1% | TabDDPM | -0.3751 | -530.0615 | -529.6864 | -366.2946 |

Interpretation: TVAE provides the strongest relative transport utility under both geometries, but all primary TSTR R² values remain negative. Synthetic augmentation therefore does not create strong absolute predictive modelability from the n=20 derivation DOE. Positive Δ must be interpreted as relative stabilization, not as evidence-equivalent replacement of experiments.

### Primary matched-n ICD (mean ± SD across 10 full realisations)

Baseline:
- Gaussian Copula: **0.6119 ± 0.0480**
- TVAE: 0.4670 ± 0.0502
- TabDDPM: 0.2911 ± 0.0847
- CTGAN: 0.2895 ± 0.0330

Sensitivity 1%:
- Gaussian Copula: **0.6150 ± 0.0703**
- TVAE: 0.4598 ± 0.0946
- TabDDPM: 0.3935 ± 0.1273
- CTGAN: 0.3082 ± 0.0432

This preserves the intended separation between predictive utility and scientific/domain concordance: TVAE ranks best for relative utility, while Gaussian Copula ranks best for preservation of the confirmed KH2PO4 effect structure and correlation geometry.

### Fidelity baseline means

- TVAE: best response marginal fidelity (KS ≈ 0.1557; Wasserstein ≈ 0.7932).
- Gaussian Copula: best correlation-of-correlations (≈ 0.8308) and high factorial-cell coverage (≈ 0.9000).
- CTGAN: weaker overall structural fidelity.
- TabDDPM: remains intrinsically unstable under the predeclared small-n configuration despite algorithmic conformance; response Wasserstein ≈ 35.91 baseline and ≈ 139.13 under sensitivity. This is retained as a scientific negative result, not tuned away.

For TabDDPM, approximately 66% (baseline) and 65% (sensitivity) of synthetic response values lie outside the observed derivation response range. No response clipping is applied, by protocol. The poor utility/fidelity therefore remains visible as part of the method stress test.

## Interpretation for manuscript revision

The final Gate 0.4 evidence does not support a narrative that synthetic expansion generally creates predictive power. It supports a more defensible claim: **trustworthy augmentation requires explicit separation of modelability, predictive transport, structural fidelity, domain-effect concordance, leakage control, and provenance**. Generator rankings are criterion-dependent, and the framework can identify when a generator is unsuitable rather than forcing a favorable winner.

## Authorization after PASS

Proceed to Gate 0.5 — final reproducibility audit and PEERFIX-Core v1.0 freeze.

External datasets may be audited for source/provenance in parallel, but no external confirmatory synthetic execution is permitted until the Core freeze is complete and the external adapter/reference-effect protocol is preregistered.
