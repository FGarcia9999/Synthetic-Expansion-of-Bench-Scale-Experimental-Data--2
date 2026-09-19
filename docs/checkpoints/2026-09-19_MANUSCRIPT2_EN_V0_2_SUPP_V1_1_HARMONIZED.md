# PEERFIX Manuscript 2 — EN v0.2 + Supplementary EN v1.1 harmonized checkpoint

Date: 2026-09-19
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
Status: **editorial harmonization / controlled English propagation only**

## 1. Governance boundary

PEERFIX-Core v1.0 remains frozen. This stage changed no Core algorithm, generator implementation, hyperparameter, seed, metric, threshold, ICD rule, downstream-model panel, adapter, confirmatory order, audit outcome, or scientific conclusion. M1 v30 remains the development manuscript and is not modified by this checkpoint. Any redesign/tuning remains future PEERFIX-Core v1.1 development/sensitivity work.

## 2. Active editorial contract

The following rules remain mandatory for M2 and its Supplementary:

1. Use short, human-readable sentences.
2. Put experimental/bioprocess meaning before computational terminology.
3. Use technical jargon only when needed for biochemical, environmental/experimental, statistical, or computational meaning; define specialized acronyms at first use.
4. Treat synthetic rows as computational records, never as new fermentations or biological replicates.
5. Preserve unfavorable and null findings; do not tune them away.
6. Keep claims generator-specific when evidence is generator-specific.
7. Separate relative improvement from absolute predictive validity.
8. M2 inherits from M1 the established separation among statistical fidelity, predictive utility, and preservation of experimental effects; M2 does not re-derive that thesis.
9. M2's distinct contribution is external transportability plus fail-closed modelability behavior under independent experimental datasets.
10. Synthetic expansion may support exploration and prioritization of relations/regions that deserve confirmation, but it does not replace bench work and does not determine an optimal future DOE by itself.
11. Literature follows the experimental interpretation, rather than leading the narrative.
12. Repository synchronization must preserve hashes, checkpoint lineage, and the frozen Core boundary.

## 3. Source writing line

Portuguese editorial source:
`Manuscrito2_PT_v0_4_PEERFIX_BIOPROCESS_FOCUS.docx`
SHA-256: `560357a46d66362ee85bd94f01344ea7d253c7e34cfd0a976586727c428ef62d`

Previous English line reviewed:
`Manuscript2_EN_v0_1_EXTERNAL_VALIDATION_PEERFIX_Core_v1.docx`

Previous English Supplementary line reviewed:
`Supplementary_Material_Manuscript2_PEERFIX_External_Validation_EN_v1.docx`

The numerical harmonization used the audited confirmatory checkpoints as authority:
- `2026-09-17_EXT_A_C_MOGII_FINAL_AUDIT.md`
- `2026-09-17_EXT_B_C_UTILIS_FINAL_PASS.md`

## 4. Final harmonized English working artifacts

### Main manuscript

`Manuscript2_EN_v0_2_PEERFIX_BIOPROCESS_FOCUS_HARMONIZED.docx`

SHA-256:
`0208990fa84dff5d21c1b6558e12b5dc8dc5e2ea8fa39031950293e20b4d29ab`

Rendered QA: **8 pages**, all visually inspected after the final text edit. No clipping, overlap, broken tables, missing glyphs, or split captions were observed.

Sentence-length audit on narrative paragraphs: approximately **14.0 words/sentence mean**, median **14**. Long technical statements were split where this improved readability without changing meaning.

### Supplementary Material

`Supplementary_Material_Manuscript2_PEERFIX_External_Validation_EN_v1_1_HARMONIZED.docx`

SHA-256:
`b238dedbacc36ff2ea7bbff31abc82ca2e8af30a9fa19eb390902ac5b264bb99`

Rendered QA: **5 pages**, all visually inspected after the final text edit. No clipping, overlap, broken tables, missing glyphs, or unreadable figure/table elements were observed.

Sentence-length audit on narrative paragraphs: approximately **11.3 words/sentence mean**, median **10**.

The first-use text now defines the domain-grounded concordance index (ICD) and distance to the closest real record (DCR), reducing unexplained computational shorthand.

## 5. Numerical reconciliation applied

Presentation values were reconciled to the audited EXT-A/EXT-B checkpoints and rounded consistently for manuscript display. No underlying result was recomputed or changed.

Examples:
- C. mogii Gaussian Copula row: TRTR `0.2589` -> `0.259`; TSTR `0.2573` -> `0.257`; Δ `-0.0016` -> `-0.002`.
- C. utilis Y1 Gaussian Copula grouped: TSTR `-0.5675` -> displayed `-0.568`.
- C. utilis Y1 TVAE row: TSTR `-0.1365` -> displayed `-0.137`.
- C. utilis Y3 CTGAN grouped: Δ `+0.5027` -> displayed `+0.503`.

These are presentation-level rounding harmonizations only.

## 6. Scientific interpretation retained

- C. mogii remains the strongest positive external result, **specifically for Gaussian Copula**. TVAE transports partially; CTGAN and TabDDPM do not sustain the same utility.
- C. utilis Y1/Y3 show relative stabilization in some generator/geometry combinations but retain negative absolute R² under the frozen LR reference.
- C. utilis Y2 remains `BLOCKED_BY_MODELABILITY`; no synthetic Y2 data exist.
- TabDDPM negative external findings remain visible and unchanged.
- The 1e-10 C. utilis recovery tolerance remains strictly a cross-runner floating-point audit tolerance; it changes no prediction, parameter, metric, threshold, or scientific rule.

## 7. Anti-salami / publication positioning

The English v0.2 carries the explicit cross-reference logic: the separation among fidelity, predictive utility, and preservation of experimental effects belongs to the M1 development study. M2 treats it as a premise and tests whether the frozen protocol transports that evaluation to independent experiments.

At submission, replace the current M1 placeholder with its real status (`submitted`, `accepted/in press`, or DOI, as appropriate and allowed by the journal).

## 8. Package

Local coauthor/submission-working package:
`PEERFIX_Manuscript2_EN_Harmonized_Package_v2.zip`

SHA-256:
`98f5c289f5d0990da1db4ddb1b184cc46a6b2f4ec07b21b78e4fc9833a72c3b3`

Package contains the harmonized English manuscript, harmonized English Supplementary, and SHA-256 manifest. Raw author-supplied workbooks are excluded.

## 9. Next technically correct stage

M2 is now ready for **coauthor scientific review of the harmonized English line** and, after that approval, **journal-specific house-style adaptation**. The next stage must not reopen Core tuning. Cover letter, highlights, CRediT, AI-use wording, and final data-availability language should be synchronized only after the target journal and final author/affiliation list are confirmed.

## Decision

**PASS — controlled English propagation and Supplementary harmonization completed.** The frozen scientific evidence is unchanged; the editorial rules remain active and are now explicitly checkpointed in the repository.