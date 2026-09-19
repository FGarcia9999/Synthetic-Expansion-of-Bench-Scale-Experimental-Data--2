# PEERFIX Manuscript 2 — v0.4 bioprocess editorial reconciliation

Date: 2026-09-19
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## Scope

This checkpoint records an **editorial/scientific-writing revision only**. PEERFIX-Core v1.0 remains frozen. No generator, seed, metric, threshold, ICD rule, downstream model, adapter, audit result, confirmatory ordering, or EXT-A/EXT-B scientific outcome was altered or retuned.

The revision reconciles the 2026-09-17 pre-writing evidence ledger, the 2026-09-18 Manuscript 2 scientific-writing line, and the 2026-09-19 M1/M2 bioprocess-focused editorial guidance.

## Source writing line

Primary source text:
`Manuscrito2_PT_v0_3c_Validacao_Externa_PEERFIX_Core_v1_REVISADO_CIENTIFICO.docx`

Companion Supplementary source:
`Material_Suplementar_Manuscrito2_PEERFIX_Validacao_Externa_PT_v1_1_REVISADO.docx`

The existing Supplementary scientific results were not retuned or recomputed in this revision.

## New Portuguese working manuscript

File:
`Manuscrito2_PT_v0_4_PEERFIX_BIOPROCESS_FOCUS.docx`

SHA-256:
`560357a46d66362ee85bd94f01344ea7d253c7e34cfd0a976586727c428ef62d`

Rendered QA PDF SHA-256:
`89f313dbc62448cd70de1c0ec02cf04a4d61d7b4ca75c3167dbbf22386503df7`

The manuscript was rendered to 9 pages and visually inspected page by page after pagination corrections. Figure legends were kept with figures, compact result tables were kept together when they fit on a page, and no clipping/overlap/missing-glyph issue was observed in the final render.

## Editorial changes applied

1. **Experimental meaning before computational terminology.** The text foregrounds medium composition, surface tension, emulsification, factor-response identifiability, DOE geometry, unseen real runs, and the need for new bench evidence.
2. **Anti-salami cross-reference.** M2 now explicitly treats the dissociation among statistical fidelity, predictive utility and preservation of experimental effects as a premise established in M1, rather than re-demonstrating it. The placeholder remains `Garcia et al., em preparação` until M1 has its real submission/publication status.
3. **Generator-specific positive claim.** The positive C. mogii transportability statement is explicitly restricted to the Gaussian Copula. TVAE is described as partial transport; CTGAN and TabDDPM remain negative external findings.
4. **Fail-closed interpretation of C. utilis Y2.** Motor-oil emulsification remains a preregistered modelability refusal before synthetic generation and is interpreted as a scientific safeguard, not as missing processing.
5. **Absolute versus relative predictive behavior.** C. utilis Y1/Y3 relative improvements remain clearly separated from their negative absolute R² values.
6. **Bioprocess decision framing.** Synthetic expansion is positioned as support for testing stability and prioritizing which relations/regions deserve confirmation in new fermentations. It is not presented as biological replication, a substitute for bench work, or an optimal-design engine.
7. **Prospective DOE safeguard.** The manuscript explicitly states that the location and number of new runs require a new experimental design and are not determined by the synthetic generator alone.
8. **Literature placement.** Helleckes et al. (2023) is used as the main bioprocess-development anchor; SynthEval/Lautrup et al. (2025) and Nanevski et al. (2026) are used only after the experimental interpretation as multi-objective synthetic-data support.

## Scientific interpretation preserved

- C. mogii remains the strongest positive external evidence, specifically for Gaussian Copula: row-CV TSTR approximately matches TRTR and grouped-condition transport remains close but lower.
- C. utilis Y1 and Y3 retain relative stabilization without strong absolute predictive validity.
- C. utilis Y2 remains `BLOCKED_BY_MODELABILITY`; no synthetic Y2 data were generated.
- TabDDPM negative external results remain visible and were not tuned away.
- Farias remains outside the required evidence chain unless its experimental-unit independence is separately clarified and preregistered.
- Any MLP redesign, optimizer search, generator/hyperparameter retuning, alternative thresholds or post-hoc model selection remains future PEERFIX-Core v1.1 development/sensitivity work.

## Supplementary consistency item before submission

The PT Supplementary v1.1 remains the current scientific companion. Before journal submission, perform a source-table reconciliation of presentation-only details such as Portuguese terminology (`row` / `grouped_condition`) and last-decimal rounding where the main manuscript and Supplementary currently display slightly different rounded values. Do **not** resolve these by ad-hoc editing; regenerate/verify both from the same audited source tables.

## Publication sequence

1. Keep M1 v30 + Supplementary as the development paper and obtain a real citable status for M1.
2. Circulate/review M2 PT v0.4 with coauthors.
3. After scientific approval, propagate the accepted PT v0.4 wording to the English M2 working line and update cover letter/highlights/data statement consistently.
4. Harmonize main manuscript and Supplementary presentation directly from audited source tables.
5. Select/adapt to the final journal house style without changing frozen scientific outcomes.

## Decision

M2 is now in **coauthor-review / pre-submission editorial consolidation**, not method-development mode. The next scientific-writing task is harmonization of the English manuscript and Supplementary against the accepted Portuguese v0.4, while PEERFIX-Core v1.0 remains unchanged.