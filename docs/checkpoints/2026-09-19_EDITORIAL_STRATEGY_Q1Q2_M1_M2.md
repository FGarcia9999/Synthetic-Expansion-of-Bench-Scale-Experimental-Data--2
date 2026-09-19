# Editorial strategy checkpoint — M1/M2 Q1/Q2 positioning

Date: 2026-09-19
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## Purpose

Consolidate the latest external Q1/Q2 reviewer feedback into the publication strategy without changing any frozen scientific result or PEERFIX-Core v1.0 rule.

## Editorial decision

Adopt the reviewer recommendation to strengthen the bioprocess-facing interpretation in both manuscripts while preserving the experimental-first narrative and keeping computational metrics subordinate to the biological/process meaning.

### M1 — development / derivation paper

Add two short paragraphs near the end of the Discussion section that translate the confirmed KH2PO4 effect and the weak absolute predictive utility into a bioprocess decision message:

- the medium-to-surface-tension relation is sufficiently stable to support formulation-oriented interpretation;
- synthetic expansion is used to stress-test stability and help prioritize future fermentations, not to replace biological replication;
- the practical endpoint is an auditable confidence criterion that combines modelability, predictive behavior, structural fidelity, domain-effect preservation and provenance.

Keep the construct discussion of ICD explicit. No post-hoc retuning or reinterpretation of negative R2 values is allowed.

### M2 — external validation paper

Add two short Discussion paragraphs connecting:

- the positive C. mogii result, where predictive behavior was preserved under a different DOE geometry;
- the C. utilis Y2 negative control, where synthetic generation was refused because the original experiment did not establish an identifiable factor-response relation.

Frame these together as a decision rule under experimental scarcity: use synthetic expansion only when the source experiment is sufficiently modelable and the external checks preserve the experimental relation; otherwise request new bench runs.

Calibrate the term `transportability`: describe the evidence as selective and geometry-sensitive rather than universal.

## Anti-salami rule

M2 must cite M1 for the general thesis that fidelity, predictive utility and domain concordance are non-equivalent objectives. M2 should not re-derive or re-prove that thesis. Its distinct contribution is external transportability plus fail-closed decision behavior under independent experimental datasets.

Submission sequence:

1. submit M1 first;
2. submit M2 only after M1 has a real citable status (`submitted`, `in press`, DOI, or equivalent allowed by target journal policy);
3. do not submit M3 until the modelability/provenance evidence is mature enough to support a standalone manuscript.

## Literature placement

Use Helleckes et al. (2023) as the principal bioprocess-development anchor. Use SynthEval (Lautrup et al.) and Nanevski et al. only as adjacent-domain support for multi-objective synthetic-data evaluation, and place them after the experimental result rather than as the narrative starting point.

## Version-control caution

The latest reviewer note was drafted against M1 v30 and an M2 v0.3c that is not currently present in this repository branch. Before directly inserting wording or numerical statements into M2, reconcile that v0.3c file against the repository/local M2 writing line to avoid parallel-version drift.

## Governance boundary

This checkpoint is editorial only. It does not modify:
- frozen Core implementation;
- generator hyperparameters;
- MLP/TabDDPM configuration;
- seeds, metrics, thresholds or ICD logic;
- EXT-A/EXT-B confirmatory outcomes;
- modelability decisions.

Any algorithmic redesign remains future PEERFIX-Core v1.1 sensitivity/development work.
