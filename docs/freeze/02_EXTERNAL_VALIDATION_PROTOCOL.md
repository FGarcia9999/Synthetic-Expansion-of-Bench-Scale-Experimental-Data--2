# PEERFIX External Validation Protocol — post-freeze

Status: preregistration framework; no external synthetic execution authorized until Gate 0.5 PASS.

## Objective

Evaluate transportability of the frozen PEERFIX-Core on independent experimental datasets without using external outcomes to alter the Core.

## Sequence

1. qualify source/provenance;
2. define the experimental unit and modelability gate;
3. freeze a dataset adapter and raw/canonical hashes;
4. freeze domain reference-effect set before synthetic generation;
5. freeze CV geometry appropriate to the external DOE;
6. execute the unchanged Core generator panel;
7. report utility, fidelity, ICD/domain concordance, DCR diagnostics, failures and provenance;
8. no external-result-driven retuning.

## Primary candidate currently qualified

The author-confirmed *Candida mogii* dataset supplied by Peterson/Jenyffer is eligible at the 27-run DOE level after Gate 0.5. The three surface-tension readings within each run remain within-run measurements, not 81 independent DOE observations.

Primary response candidate: `STred`.

Author/source-confirmed quadratic-effect fingerprint available for preregistration:
- D (yeast extract): positive;
- AB: negative;
- AD: positive;
- BC: negative;
- BD: negative.

CD (p≈0.068 in source model) is not part of the primary confirmed set unless explicitly declared secondary before execution.

## Other candidates

- Farias et al. (2021): remains conditional pending clarification of `SAMPLES 1–5` independence and relation to triplicate/four-experiment descriptions.
- *Candida utilis* dataset associated with Lívia/Jenyffer: remains pending author/source clarification of factor-label semantics/provenance.

## External Core invariants

External data may not change generator families, generator hyperparameters, deterministic seed map, leakage rules, downstream model seed comparability, primary metrics, matched-n ICD logic, primary lambda, DCR diagnostic-only rule, failure handling, or provenance serialization/hashing.

## Interpretation

External validation asks whether the frozen method transports. It is not a second development stage. A failure to transport is reportable evidence and does not authorize retuning within the confirmatory analysis.
