# EXT-A — Candida mogii confirmatory external validation — PASS

Date: 2026-09-16
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
Authorized execution commit: `6835f7f43c63f07070fe58d611707435371d5e18`
GitHub Actions run: `35142610014`

## Decision

**PASS for execution and integrity conformance.** The final audit reported 1030 checks, 0 failures, across Gaussian Copula, CTGAN, TVAE and TabDDPM, under both row and grouped-condition CV geometries. This PASS does not assert that every generator transports scientifically well; transportability is interpreted from the frozen metrics without post-hoc retuning.

## Integrity evidence

- Preflight: PASS, including frozen-Core verification and external adapter contract tests.
- Four scientific generator jobs: PASS.
- Final audit job: PASS.
- Artifact `external-a-audit-6835f7f43c63f07070fe58d611707435371d5e18`: ID `10467230453`; digest `sha256:5ab2cd2d32cb201c2c64d31c4fd3a2dfd7489714c27ef5a9c0080a2c828cfb75`.
- Generator artifact digests:
  - Gaussian Copula: `sha256:3ef0651e903e9981563a52a03030bcb843445ab9cff170ec80f729353087e022`
  - CTGAN: `sha256:d57a3099aeaefaac31899c19391015e654efda6624d1dd994a1ec521b088b40a`
  - TVAE: `sha256:6c438a489daea2e10140744a91ebae58493d3eb45b01bd29864fc15b338ce13b`
  - TabDDPM: `sha256:3f8bad7c19ed5f1e6b8b9ae5d22872d3afc9404075b978f45aeed0a3add7aed1`
- Repository comparison against the frozen Core anchor is strictly ahead by 14 commits and modifies/adds only external-validation workflow/config/data/runner/audit/test/checkpoint files; no frozen scientific Core file is changed.

## Scientific findings under the frozen protocol

Mean external metrics from the audit artifact:

| Generator | CV geometry | TRTR R² | TSTR R² | ΔR²=TSTR−TRTR | AUGTR R² | AUGTR−TRTR | ICD mean | KS mean | Wasserstein mean | corr-of-corr | DOE coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Gaussian Copula | row | 0.2589 | 0.2573 | -0.0016 | 0.2649 | +0.0060 | 0.3478 | 0.1665 | 0.8003 | 0.9597 | 0.392 |
| Gaussian Copula | grouped | 0.3172 | 0.2809 | -0.0363 | 0.2919 | -0.0253 | 0.3478 | 0.1665 | 0.8003 | 0.9597 | 0.392 |
| CTGAN | row | 0.2589 | -0.2010 | -0.4598 | 0.0392 | -0.2197 | 0.2481 | 0.3632 | 2.6153 | 0.4033 | 0.324 |
| CTGAN | grouped | 0.3172 | -0.3560 | -0.6731 | -0.0988 | -0.4160 | 0.2481 | 0.3632 | 2.6153 | 0.4033 | 0.324 |
| TVAE | row | 0.2589 | 0.1877 | -0.0712 | 0.2374 | -0.0215 | 0.2900 | 0.1755 | 0.9310 | 0.7318 | 0.428 |
| TVAE | grouped | 0.3172 | 0.2032 | -0.1140 | 0.2617 | -0.0555 | 0.2900 | 0.1755 | 0.9310 | 0.7318 | 0.428 |
| TabDDPM | row | 0.2589 | -229.4513 | -229.7102 | -184.7627 | -185.0215 | 0.2233 | 0.5159 | 60.2073 | 0.3785 | 0.100 |
| TabDDPM | grouped | 0.3172 | -440.5859 | -440.9030 | -333.2773 | -333.5944 | 0.2233 | 0.5159 | 60.2073 | 0.3785 | 0.100 |

Interpretation fixed after observing the preregistered execution: Gaussian Copula shows the strongest utility transport on EXT-A, with TSTR close to TRTR in row CV and a modest degradation under grouped-condition CV. TVAE retains partial utility but degrades relative to TRTR. CTGAN transports poorly on this dataset. TabDDPM is a clear external failure under the frozen configuration despite having the lowest mean ICD; therefore low ICD alone is not evidence of predictive/DOE transportability. No generator, threshold, seed, reference effect, metric, or Core rule is retuned from these outcomes.

## Next authorized phase

Proceed to preregistered EXT-B (`Candida utilis`) on this branch. Y1 is the primary positive/modelable block; Y3 is secondary concordance; Y2 remains a fail-closed negative-control and **must not** receive synthetic generation. EXT-B must use the unchanged frozen Core and the same integrity rules before any interpretation.