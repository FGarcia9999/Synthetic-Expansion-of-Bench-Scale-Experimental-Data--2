# PEERFIX Manuscript 2 — v0.3c scientific-writing checkpoint

Date: 2026-09-18
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## Scope

This checkpoint records an editorial/scientific rewrite only. No PEERFIX-Core v1.0 implementation, adapter, generator setting, seed, metric, threshold, audit result, or confirmatory outcome was changed.

## Working manuscript

Portuguese working file:
`Manuscrito2_PT_v0_3c_Validacao_Externa_PEERFIX_Core_v1_REVISADO_CIENTIFICO.docx`

Local SHA-256:
`873a7b0db5471abb8694a95ec03e9782d63d287a052843b4e3cdf2edfc048013`

## Editorial changes

- Reframed the manuscript around the experiments and measured responses rather than computational jargon.
- Clarified that synthetic rows are not new fermentations or biological replicates.
- Added experimental context from the source studies: C. mogii central composite design and strong surface-tension model; C. utilis factorial design with response-specific modelability.
- Replaced “baseline” wording in key passages with explicit descriptions of models trained on real runs.
- Explained negative R² in plain experimental terms.
- Moved cross-runner MLP numerical-equivalence detail out of the main Results narrative and left it for Supplementary/audit documentation.
- Strengthened the interpretation of Y2 as a scientifically meaningful refusal to generate when the source experiment does not support the requested factor-response relation.
- Added a concise description and bibliographic provenance of Gaussian Copula/SDV, CTGAN/TVAE and TabDDPM without changing their frozen implementations.
- Expanded references to include current synthetic-data evaluation work and original methodological sources.
- Refined the data-availability language to distinguish explicit C. mogii use authorization from the C. utilis coauthor/corresponding-author collaboration context; public redistribution is not assumed for either raw workbook.
- Removed the obsolete editorial callout that had created an otherwise empty final page.
- Preserved all frozen EXT-A and EXT-B numerical results and the no-retuning firewall.

## Scientific interpretation preserved

- C. mogii remains the strongest positive external transportability result, with Gaussian Copula TSTR nearly matching TRTR under row CV and remaining close under grouped-condition CV.
- C. utilis Y1 and Y3 show relative stabilization but not strong absolute predictive validity.
- C. utilis Y2 remains `BLOCKED_BY_MODELABILITY`; no synthetic generation occurred.
- TabDDPM negative external results remain visible and are not tuned away.

## Supplementary writing state

Portuguese Supplementary revised file:
`Material_Suplementar_Manuscrito2_PEERFIX_Validacao_Externa_PT_v1_1_REVISADO.docx`

Local SHA-256:
`3eef7b07192536c63b3d0e71c6f7583af8d46756661bb21a38da7332f93d203b`

The Supplementary was tightened to emphasize experimental meaning, preserve the Y2 refusal as a scientific result, and keep GitHub cross-runner numerical-equivalence details outside the main manuscript.

## Layout QA

The v0.3c manuscript was rendered to 9 pages and visually inspected page by page. The Supplementary v1.1 was rendered to 5 pages and visually inspected. No clipping, overlap, broken figures, broken tables, or missing glyphs were observed.

## Remaining editorial work

- coauthor review of scientific interpretation and authorship order;
- final target-journal selection and house-style adaptation;
- English version only after the Portuguese scientific text is accepted by the coauthors;
- final cover letter/highlights/data statement after journal selection;
- Farias remains optional and outside the required evidence chain until author clarification.
