# PEERFIX project-wide scientific evidence ledger — pre-writing checkpoint

Date: 2026-09-17
Status: **pre-writing evidence consolidation**
Frozen Core: `PEERFIX-Core v1.0`, anchor `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## 1. Governance boundary

PEERFIX-Core v1.0 is frozen. Confirmatory external outcomes do not modify its algorithms, generator hyperparameters, seeds, leakage rules, metrics, ICD definition/thresholds, reference effects or confirmatory order. Any MLP redesign, alternative architecture, optimizer search, Bayesian/Optuna tuning, or other algorithmic improvement belongs only to a future **PEERFIX-Core v1.1 sensitivity/development study** and must not reinterpret v1.0 confirmatory evidence.

## 2. PEERFIX2 — derivation/development evidence

Qualified derivation dataset: `n=20`, full `2^4` factorial + 4 center runs; canonical SHA-256 `c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`. Frozen primary CV = repeated K-fold 5×10; structural CV = grouped-condition 5×10; primary reference = linear regression; four frozen generators = Gaussian Copula, CTGAN, TVAE and PEERFIX small-n TabDDPM; matched-n ICD required; DCR diagnostic only; no external-outcome retuning.

Gate 0.4 validated canonical round-trip provenance, completeness, leakage-free execution, downstream TRTR invariance, seed uniqueness, 10/10 unique Gaussian Copula realizations and TabDDPM algorithmic conformance. Gate 0.5 freeze audit run `34984504198` passed the full contract suite (35 tests) and protected implementation check. Freeze audit artifact SHA-256: `47e6611fda5d0510fb622594d92e535f90c1ab79ebbe0590f78bf72ad9a3229a`.

**Manuscript implication:** PEERFIX2 supports the framework as a reproducible, leakage-controlled, multi-objective method for small experimental datasets. Synthetic fidelity/domain concordance, predictive utility and proximity/DCR must remain distinct claims; synthetic rows are not new biological replication.

## 3. EXT-A — C. mogii — publication-ready confirmatory evidence

Run `35142610014`, execution commit `6835f7f43c63f07070fe58d611707435371d5e18`: preflight + four generators + final audit PASS, `1030` checks and `0` failures. Audit artifact SHA-256 `5ab2cd2d32cb201c2c64d31c4fd3a2dfd7489714c27ef5a9c0080a2c828cfb75`.

Frozen LR findings: Gaussian Copula transports best (row TRTR R² `0.2589`, TSTR `0.2573`, Δ `-0.0016`; grouped TRTR `0.3172`, TSTR `0.2809`, Δ `-0.0363`; corr-of-corr `0.9597`). TVAE transports partially. CTGAN transports poorly. TabDDPM fails severely despite the lowest matched-n ICD (`0.2233`), demonstrating that low ICD alone is insufficient evidence of predictive/DOE transportability.

**Manuscript implication:** this is the strongest positive external transportability evidence, but it is generator-selective and geometry-sensitive. It supports a multi-objective interpretation rather than a claim that synthetic expansion is universally beneficial.

## 4. EXT-B — C. utilis — publication-ready confirmatory/modelability evidence

Source scientific run `35188098365`, commit `2f7565ee0c5ee5e472e0dc5750d86e6c8feee515`; eight authorized jobs Y1/Y3 × four generators completed. Audit-only recovery run `35212132316`, commit `138a7dd2ebac0ce716bec92c8d184a9c4a031372`, reused those original artifacts and reran no generators. Recovery audit artifact SHA-256 `d561c29464714ce19d8ead2c161d693d674a962a24897791c22c3a3ca9e7fa48`; Y1 and Y3 each passed `1030/1030` audit checks.

The `1e-10` TRTR tolerance is strictly an **engineering cross-runner floating-point numerical-equivalence tolerance**. It does not change any scientific metric, threshold, prediction, model, generator or outcome. Observed maximum differences were `1.5653256468795007e-11` (Y1) and `1.0658141036401503e-13` (Y3).

Y1 primary block: real-only LR baselines are negative (row `-0.3188`, grouped `-0.5899`). Gaussian Copula is approximately neutral/slightly better (Δ `+0.0052`, `+0.0224`); TVAE improves relative to baseline (Δ `+0.1824`, `+0.4361`) but remains negative in absolute R²; CTGAN is mixed/degrading; TabDDPM fails catastrophically. Y3 secondary block likewise has negative TRTR (`-0.9144`, `-1.0390`); Gaussian/CTGAN/TVAE improve relative to baseline but remain negative in absolute R², so these are not strong predictive-validity claims.

Y2 is the prespecified negative-control: **BLOCKED_BY_MODELABILITY**, no synthetic generation. This is publication-relevant fail-closed evidence that PEERFIX can refuse an unsupported factor-response relation rather than manufacture one.

**Manuscript implication:** EXT-B is more valuable as robustness/modelability evidence than as positive absolute predictive validation. Relative gains against negative baselines must be stated cautiously.

## 5. PEERFIX4 / modelability status

PEERFIX4/Ivison remains a provenance/modelability stress-validation component, not a source for retroactive Core tuning. Its role in the manuscript should emphasize eligibility, traceability, experimental-unit definition and fail-closed decisions when relation identifiability is inadequate. Only source-reconciled evidence should be promoted to confirmatory status.

Farias remains **optional/held out** pending Charles's clarification of the experimental meaning and independence of `SAMPLES 1–5`; no manuscript claim should depend on it at this stage.

## 6. Publication-ready evidence versus future sensitivity work

### Publication-ready now

- Frozen PEERFIX-Core v1.0 provenance and reproducibility chain through Gates 0.4/0.5.
- PEERFIX2 derivation results under the frozen protocol.
- EXT-A C. mogii selective external transportability, especially Gaussian Copula, plus negative CTGAN/TabDDPM findings.
- EXT-B C. utilis Y1/Y3 audited robustness findings with careful absolute-vs-relative utility interpretation.
- EXT-B Y2 `BLOCKED_BY_MODELABILITY` as a prespecified negative-control result.
- Evidence that ICD/fidelity/domain concordance and predictive utility are non-equivalent objectives.
- Explicit negative findings retained without post-hoc retuning.

### Future sensitivity/development only — not part of v1.0 confirmatory interpretation

- MLP redesign/tuning, architecture search, optimizer changes, Bayesian/Optuna tuning.
- Retuning TabDDPM for small external datasets.
- Alternative thresholds, ICD weights, seeds or generator hyperparameters.
- Additional downstream models chosen after observing EXT-A/EXT-B outcomes.
- Farias execution unless/until SAMPLES 1–5 are author-clarified and preregistered.

Any such work must be versioned as PEERFIX-Core v1.1 or later and reported as sensitivity/development, not as a correction of v1.0 confirmatory results.

## 7. Provenance/integrity state at pre-writing checkpoint

The external branch is a strict descendant of frozen Core anchor `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`. Repository comparison shows only external-validation additions; no file under `peerfix_core/` and no pre-existing frozen protocol/configuration file changed. Canonical external adapters preserve dataset provenance and prohibit assumed public redistribution of author-supplied raw workbooks.

## 8. Remaining work before manuscript rewriting

1. Freeze this ledger/checkpoint as the sole pre-writing evidence map and use exact run/commit/artifact identities in Methods/Supplementary.
2. Reconcile manuscript biological naming/source lineage consistently with the qualified PEERFIX2 dataset; do not reuse obsolete manuscript identity text.
3. Rewrite Methods around the frozen Core and external-validation firewall, including adapter preregistration, run-level experimental units, leakage-free CV, matched-n ICD, DCR's diagnostic-only role and fail-closed modelability.
4. Rewrite Results in three layers: PEERFIX2 derivation; EXT-A transportability; EXT-B robustness/modelability. Separate integrity PASS from scientific performance.
5. State negative findings explicitly, especially TabDDPM external failure and weak/negative EXT-B absolute LR utility.
6. Update figures/tables and Supplementary directly from frozen/audited artifacts, with hashes and provenance manifest.
7. Harmonize authorship/CRediT, licensing/data-redistribution language, README/CITATION/Zenodo metadata before submission.
8. Keep Farias outside the required evidence chain unless Charles resolves SAMPLES 1–5 in time for a separately preregistered optional analysis.

**Pre-writing decision:** the evidence base is sufficient to begin manuscript rewriting without changing PEERFIX-Core v1.0.