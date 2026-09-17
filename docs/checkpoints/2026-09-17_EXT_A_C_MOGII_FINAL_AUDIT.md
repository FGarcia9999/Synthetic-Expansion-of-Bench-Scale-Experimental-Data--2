# PEERFIX EXT-A — C. mogii final external-validation audit

Date: 2026-09-17
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
Execution commit: `6835f7f43c63f07070fe58d611707435371d5e18`
Workflow run: `35142610014`
Decision: **PASS — execution/integrity; scientific transportability interpreted from frozen metrics without retuning**

## Integrity result

The preflight, all four generator jobs and the final audit completed successfully. The audit evaluated 1,030 checks with 0 failures. It verified complete 5-fold × 10-repeat row and grouped-condition CV, complete 27-row held-out coverage in each repeat/model/regime, canonical dataset hash identity, generator status, 10 distinct seeds and 10 distinct synthetic hashes per generator, complete matched-n ICD/fidelity outputs, and exact TRTR invariance across generator labels within each geometry.

The branch remains a strict descendant of the frozen Core commit. Comparison against `0d5a73d...` shows only external-validation additions; no file under `peerfix_core/`, no frozen protocol file, and no frozen requirement file changed.

## Artifact identities

- Audit: `external-a-audit-6835f7f43c63f07070fe58d611707435371d5e18`
  - artifact id: `10467230453`
  - SHA-256: `5ab2cd2d32cb201c2c64d31c4fd3a2dfd7489714c27ef5a9c0080a2c828cfb75`
- Gaussian Copula: artifact id `10465918278`, SHA-256 `3ef0651e903e9981563a52a03030bcb843445ab9cff170ec80f729353087e022`
- CTGAN: artifact id `10466129918`, SHA-256 `d57a3099aeaefaac31899c19391015e654efda6624d1dd994a1ec521b088b40a`
- TVAE: artifact id `10465938350`, SHA-256 `6c438a489daea2e10140744a91ebae58493d3eb45b01bd29864fc15b338ce13b`
- TabDDPM: artifact id `10466167675`, SHA-256 `3f8bad7c19ed5f1e6b8b9ae5d22872d3afc9404075b978f45aeed0a3add7aed1`

## Scientific findings — primary frozen LR reference

### Row CV

| Generator | TRTR R² | TSTR R² | AUGTR R² | Δ TSTR−TRTR | ICD | KS | Corr-of-corr | DOE cell coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gaussian Copula | 0.2589 | 0.2573 | 0.2649 | -0.0016 | 0.3478 | 0.1665 | 0.9597 | 0.392 |
| TVAE | 0.2589 | 0.1877 | 0.2374 | -0.0712 | 0.2900 | 0.1755 | 0.7318 | 0.428 |
| CTGAN | 0.2589 | -0.2010 | 0.0392 | -0.4598 | 0.2481 | 0.3632 | 0.4033 | 0.324 |
| TabDDPM | 0.2589 | -229.4513 | -184.7627 | -229.7102 | 0.2233 | 0.5159 | 0.3785 | 0.100 |

### Grouped-condition CV

| Generator | TRTR R² | TSTR R² | AUGTR R² | Δ TSTR−TRTR |
|---|---:|---:|---:|---:|
| Gaussian Copula | 0.3172 | 0.2809 | 0.2919 | -0.0363 |
| TVAE | 0.3172 | 0.2032 | 0.2617 | -0.1140 |
| CTGAN | 0.3172 | -0.3560 | -0.0988 | -0.6731 |
| TabDDPM | 0.3172 | -440.5859 | -333.2773 | -440.9030 |

## Interpretation

EXT-A provides a genuine positive transportability result for **Gaussian Copula** under a different DOE geometry: its TSTR is essentially equal to the real-only LR baseline in row CV and remains close in the stricter grouped-condition geometry; augmentation is neutral/slightly positive in row CV and mildly negative under grouped-condition CV. Gaussian Copula also shows the strongest correlation preservation (`corr-of-corr ≈ 0.960`).

TVAE transports partially: it remains positive in both CV geometries but loses utility relative to TRTR. CTGAN does not transport adequately under the frozen utility criterion. TabDDPM again fails severely in the small-n regime; because the frozen algorithm passed prior conformance tests and no external tuning is allowed, this is retained as a legitimate negative external finding.

The matched-n ICD values are modest rather than near-perfect. This is scientifically important: external predictive transportability and exact preservation of all source-domain effect fingerprints are not equivalent properties, reinforcing the multi-objective PEERFIX interpretation.

## Decision and next phase

EXT-A is closed as **PASS for integrity and evidence of selective external transportability**, without selecting or retuning a generator post hoc. The preregistered next phase is EXT-B / C. utilis. Y1 is executed as the primary positive block; Y3 as the secondary concordance block; Y2 remains a prespecified modelability negative control and synthetic generation is prohibited for Y2.
