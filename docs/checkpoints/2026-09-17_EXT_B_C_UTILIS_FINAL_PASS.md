# PEERFIX EXT-B — C. utilis final confirmatory checkpoint — PASS

Date: 2026-09-17
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
Source scientific run: `35188098365`
Source scientific commit: `2f7565ee0c5ee5e472e0dc5750d86e6c8feee515`
Audit-only recovery run: `35212132316`
Recovery authorization commit: `138a7dd2ebac0ce716bec92c8d184a9c4a031372`
Decision: **PASS for execution/integrity; scientific interpretation remains frozen and no post-outcome retuning is permitted.**

## Recovery provenance and audit decision

The source run completed preflight and all eight authorized scientific jobs: Y1 and Y3 × Gaussian Copula, CTGAN, TVAE and TabDDPM. Y2 was the preregistered modelability negative control and remained `BLOCKED_BY_MODELABILITY`; no synthetic data were generated for Y2.

The original audit stopped on an overly strict cross-runner TRTR equality threshold of `1e-12`. The observed maximum discrepancy was approximately `1.565e-11`, arising in the MLP baseline across separately scheduled runners. Recovery run `35212132316` downloaded and reused the original scientific artifacts from run `35188098365`; **no generator or scientific job was rerun**. It audited Y1 and Y3 with absolute tolerance `1e-10` solely for cross-runner floating-point numerical equivalence. This tolerance is an **engineering audit tolerance only**: it does not change PEERFIX-Core v1.0 scientific rules, generator hyperparameters, seeds, predictions, metrics, thresholds, reference effects, confirmatory order or outcomes.

Recovered audits: Y1 `1030/1030 PASS`, Y3 `1030/1030 PASS`. Y1 maximum TRTR cross-runner absolute difference = `1.5653256468795007e-11`; Y3 maximum = `1.0658141036401503e-13`. Recovery audit artifact `external-b-audit-recovery-138a7dd2ebac0ce716bec92c8d184a9c4a031372`, ID `10492843054`, SHA-256 `d561c29464714ce19d8ead2c161d693d674a962a24897791c22c3a3ca9e7fa48`.

## Original scientific artifact identities — run 35188098365

- Y1 Gaussian Copula: `sha256:e0c42c069c15562684cb44e2b40cb8bb56147bea0fdd33ebc957549da9a70007`
- Y1 CTGAN: `sha256:71f70f5b528381b807f3848b9263bbc2fe62eac0538906e1f8832c1f7c6ba974`
- Y1 TVAE: `sha256:1f3d5429e96ae57fe4f727495abd5b9dbd253979f9d065edeaaaf0dae42b668e`
- Y1 TabDDPM: `sha256:b6f7ded0e7c30416e4be45376ad664d819545aae2aef1ccd810c31b27d99feb8`
- Y3 Gaussian Copula: `sha256:35e8c1bf7cee4528278cb3ab850704794e214ef56807f1c6537f865da8775e8d`
- Y3 CTGAN: `sha256:c200c1855edfe2a7b3c40e8757bc1d5e95f9b6f9c878bdab6e246ea1014e5b07`
- Y3 TVAE: `sha256:f6b1bdd67fe3fd2ca85ceef106ee2ceba2e0a7a66431c98344cf1517eb68ea9b`
- Y3 TabDDPM: `sha256:d812c99fe168cf24c9a219eff20b0d6d4a06eb874c7cf81b63db4d02d25e4b5f`

## Scientific summary — frozen primary LR reference

### Y1 surface tension — primary positive/modelable block

| Generator | Geometry | TRTR R² | TSTR R² | AUGTR R² | Δ TSTR−TRTR | ICD | KS | corr-of-corr | DOE coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gaussian Copula | row | -0.3188 | -0.3137 | -0.2854 | +0.0052 | 0.4253 | 0.1974 | 0.8096 | 0.9412 |
| Gaussian Copula | grouped | -0.5899 | -0.5675 | -0.5439 | +0.0224 | 0.4253 | 0.1974 | 0.8096 | 0.9412 |
| CTGAN | row | -0.3188 | -0.5282 | -0.4048 | -0.2094 | 0.2734 | 0.3980 | -0.1792 | 0.6941 |
| CTGAN | grouped | -0.5899 | -0.6423 | -0.4750 | -0.0524 | 0.2734 | 0.3980 | -0.1792 | 0.6941 |
| TVAE | row | -0.3188 | -0.1365 | -0.1024 | +0.1824 | 0.3234 | 0.1983 | 0.4934 | 0.6353 |
| TVAE | grouped | -0.5899 | -0.1538 | -0.1428 | +0.4361 | 0.3234 | 0.1983 | 0.4934 | 0.6353 |
| TabDDPM | row | -0.3188 | -34680.3640 | -47128.4529 | -34680.0451 | 0.2626 | 0.5671 | 0.2108 | 0.6235 |
| TabDDPM | grouped | -0.5899 | -8415.5180 | -15681.0757 | -8414.9281 | 0.2626 | 0.5671 | 0.2108 | 0.6235 |

Y1 therefore passes integrity/modelability gating but is a difficult predictive small-n external block: the real-only LR baseline itself is negative. Gaussian Copula is approximately neutral/slightly positive relative to TRTR; TVAE improves relative to the negative baseline while remaining negative in absolute R²; CTGAN degrades; TabDDPM fails severely under the frozen configuration. These are confirmatory outcomes and are retained without retuning.

### Y3 E24 canola — secondary concordance block

| Generator | Geometry | TRTR R² | TSTR R² | AUGTR R² | Δ TSTR−TRTR | ICD | KS | corr-of-corr | DOE coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gaussian Copula | row | -0.9144 | -0.7314 | -0.7105 | +0.1830 | 0.3049 | 0.2834 | 0.2914 | 0.9412 |
| Gaussian Copula | grouped | -1.0390 | -0.7654 | -0.7522 | +0.2737 | 0.3049 | 0.2834 | 0.2914 | 0.9412 |
| CTGAN | row | -0.9144 | -0.6244 | -0.5269 | +0.2900 | 0.2630 | 0.2955 | 0.1866 | 0.6588 |
| CTGAN | grouped | -1.0390 | -0.5363 | -0.4691 | +0.5027 | 0.2630 | 0.2955 | 0.1866 | 0.6588 |
| TVAE | row | -0.9144 | -0.5998 | -0.5555 | +0.3146 | 0.3227 | 0.2414 | 0.2414 | 0.6235 |
| TVAE | grouped | -1.0390 | -0.5328 | -0.5381 | +0.5062 | 0.3227 | 0.2414 | 0.2414 | 0.6235 |
| TabDDPM | row | -0.9144 | -16806.9437 | -22203.9459 | -16806.0293 | 0.2317 | 0.4688 | 0.0939 | 0.6176 |
| TabDDPM | grouped | -1.0390 | -9486.5529 | -7762.5066 | -9485.5138 | 0.2317 | 0.4688 | 0.0939 | 0.6176 |

Y3 also has a negative real-only LR baseline. Gaussian Copula, CTGAN and TVAE improve relative to that baseline but remain negative in absolute R²; TabDDPM again fails severely. Relative improvement against a negative baseline must not be presented as strong predictive validity.

## Y2 negative control

Y2 E24 motor oil was preregistered as a modelability negative control (`source_global_p = 0.69`, no valid factor-response relation). Its status is **BLOCKED_BY_MODELABILITY**. Synthetic generation for Y2 is prohibited and did not occur. This is positive evidence that the modelability gate can refuse an unsupported response instead of manufacturing a synthetic confirmatory relation.

## Repository/Core integrity

Comparison of this external branch against frozen anchor `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1` is a strict descendant relationship. Changes are confined to external-validation adapters/data/workflows/runners/auditors/tests/checkpoints. No file under `peerfix_core/` and no pre-existing frozen protocol/configuration file was modified. The frozen manifest `config/01_PEERFIX_CORE_v1_FROZEN.yaml` retains its original Core identities and Gate 0.4/0.5 evidence.

## Decision

**EXT-B PASS for execution and integrity.** Scientific evidence is mixed and intentionally preserved: Y1/Y3 demonstrate that synthetic generators can improve relative utility against weak negative real-only LR baselines without establishing strong absolute predictive validity; Gaussian Copula retains strong DOE coverage, while TabDDPM is consistently unsuitable under the frozen small-n configuration. Y2 supplies the prespecified fail-closed modelability result. No confirmatory outcome is used to redesign PEERFIX-Core v1.0.