# PEERFIX external validation — preregistration

Date: 2026-09-16
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
Core status: **PEERFIX-Core v1.0 FROZEN / Gate 0.5 PASS**

## Purpose

This document freezes the external-validation sequence **before any external generator execution**. The external datasets may change schema mapping, experimental-unit definitions, grouping, support and domain-reference relations through adapters, but they may not change the frozen PEERFIX-Core algorithms, generator families/hyperparameters, leakage rules, seed policy, primary metrics, ICD logic, lambda, or failure policy.

## Confirmatory order

1. **EXT-A — Candida mogii / Peterson et al.**: primary transportability test under a different DOE geometry (27-run four-factor central composite design, alpha=2). Canonical response: `STred` at run level.
2. **EXT-B — Candida utilis / Livia et al.**: independent multiresponse external challenge under a full 2^4 factorial + 3 centers (19 runs). Primary positive block: Y1 surface tension; prespecified negative-control/modelability block: Y2 E24 motor oil; secondary positive-domain block: Y3 E24 canola.
3. **Farias et al.** remains held out and is not included in execution until the authors clarify the experimental meaning/independence of `SAMPLES 1–5`.

## Frozen external-comparison rules

- No generator or downstream-model retuning from external outcomes.
- No threshold retuning, seed cherry-picking, metric substitution, or post-hoc change of reference effects.
- Gaussian Copula, CTGAN, TVAE and PEERFIX small-n TabDDPM are used with the frozen Core implementations/hyperparameters.
- Primary utility uses the frozen low-variance linear-regression reference model; RF/GBR/MLP remain fixed secondary models.
- Fold-refit is mandatory: the generator is fit only on the real training fold.
- Repeated CV: 5 folds x 10 repeats where geometrically feasible; exact-factor-tuple grouped sensitivity keeps replicated center conditions together.
- TRTR, TSTR and AUGTR use the same held-out real rows within each comparison.
- External primary synthetic sample size: **140 rows per fitted generator**, retained as a fixed computational-comparability setting and explicitly not interpreted as 140 biological experiments.
- ICD uses matched effective n equal to the external real run count (27 for EXT-A; 19 for EXT-B), preserving the frozen matched-n principle.
- DCR remains diagnostic only.
- Raw author-supplied workbooks are not committed to the public repository without separate explicit redistribution permission; their SHA-256 identities are recorded in the adapters.

## Decision logic

The external phase asks whether the already-frozen Core transports, not whether it can be optimized to each new dataset. Therefore negative or mixed results are valid confirmatory outcomes. A generator can show statistical fidelity yet fail utility or scientific concordance; a response block can also correctly fail the modelability/relationship test.

## Execution firewall

External generator execution is authorized only from commits that contain this preregistration and the corresponding dataset adapter. Any later scientific-rule change requires a new protocol version and must not be represented as confirmatory PEERFIX-Core v1.0 validation.
