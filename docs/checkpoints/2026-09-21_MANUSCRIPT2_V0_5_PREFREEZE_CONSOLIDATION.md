# PEERFIX Manuscript 2 — v0.5 pre-freeze consolidation

Date: 2026-09-21
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## Scope

This checkpoint consolidates the Manuscript 2 pre-freeze scientific-writing line after the second technical-review round, terminology review, additional literature contrast for emulsification/modelability, and the partial author clarification for the Farias dataset.

**No PEERFIX-Core v1.0 file, generator, seed, metric, threshold, ICD rule, predictive model, adapter, or confirmatory outcome was altered or retuned.**

## Current pre-freeze artifacts

- `Manuscript2_EN_v0_5_PREFREEZE.docx`
  - SHA-256: `bec1447a8c5237c2398643490a41f0f0bda246d771c1b72156302847aaf486f0`
- `Manuscrito2_PT_v0_5_PREFREEZE.docx`
  - SHA-256: `2d8e2991b42cd2ad5b39404577c25e55760254ae9fbf8cd68ef76bc6b77a5c1e`
- `Supplementary_Material_Manuscript2_EN_v1_3_PREFREEZE.docx`
  - SHA-256: `c4e5c6906e862b3fefbd103321cee6087d2a3923574ec707a18a38cb394eb8b0`
- `Relatorio_Ajustes_M2_v0_5_PREFREEZE.docx`
  - SHA-256: `1666084c500de8bd3ddd3a797e31fb71e7dc3c1c30b027c508775dcbbd584bce`
- `Matriz_Resolucao_Comentarios_M2_v0_5_PREFREEZE.docx`
  - SHA-256: `f1e2787a43afcf8201a8c52a3aadc26d873420c6291850b788ab038dbdcbfb16`

## Scientific/editorial changes incorporated

### 1. Bioprocess/laboratory terminology sweep

Reader-facing language was revised to avoid literal translations or unnecessarily narrow data-science jargon.

Examples:
- PT `corridas` -> `ensaios experimentais`, `dados experimentais`, or `unidade experimental` according to context.
- EN `real runs` / `held-out real runs` -> `experimental data`, `experimental validation set`, or equivalent.
- `run-wise` -> `experiment-wise` where the scientific unit is the experimental unit.
- `Adding rows` -> `Synthetic data augmentation` in the manuscript narrative.

Technical identifiers such as GitHub Actions `run ID` remain unchanged when they refer to software-execution metadata rather than laboratory experiments.

### 2. C. mogii claim calibration

The positive external C. mogii result remains explicitly generator-specific and primarily predictive for Gaussian Copula.

The manuscript/Supplementary now state that:
- ICD = 0.348;
- design-space coverage = 0.392;
- correlation-of-correlations = 0.960.

Therefore, `selective positive transportability` must not be read as global validation of every fidelity/concordance dimension. The result is strongest on held-out experimental predictive utility, while domain concordance and coverage remain moderate.

### 3. C. utilis Y3 remains secondary only

No attempt was made to promote Y3 to primary evidence.

- The published source article describes the emulsification models as non-significant/non-predictive.
- The preregistered author-supplied workbook retains a glucose x yeast-extract interaction for the secondary conditional block.
- Y3 remains secondary conditional concordance/robustness evidence only.
- Formal source-author provenance confirmation is still required before final scientific freeze.
- If that confirmation is not documentable, the conservative pre-agreed action is to move Y3 to Supplementary-only exploratory reporting and exclude it from main modelability claims.

### 4. Literature contrast added to Discussion

The Discussion now makes clear that limited prediction for C. utilis emulsification responses should not be interpreted as an intrinsic impossibility of predicting emulsification.

The contrast uses:
- Araújo et al. (2025): C. utilis source study; emulsification responses not supported as predictive models in the published analysis.
- Albuquerque et al. (2006): initial factorial analysis showed curvature/inadequacy of the linear approximation; a subsequent second-order design supported a significant predictive bioemulsification model.
- Fontes et al. (2010): Yarrowia lipolytica study with factorial/response-surface design; predictive quadratic models for emulsification and surface-tension responses.

The scientific conclusion is experiment- and design-specific: prediction should not be forced when the available experimental design does not identify a stable factor-response relationship.

### 5. Farias author clarification incorporated without reopening M2 scope

A direct clarification from Charles Farias indicates that five cultivation conditions were used for each experiment, with specific agitation/rotation, fermentation time and growth temperature, and that these conditions were performed in triplicate.

This improves the interpretation of `SAMPLE 1-5`, but does not yet prove the exact mapping between spreadsheet rows and independent experimental units.

Current decision:
- Farias remains outside the required M2 confirmatory evidence chain.
- The M2 is not reopened to add a third external dataset.
- If the final SAMPLE-to-condition/replicate mapping is confirmed, Farias becomes a strong candidate for prospective post-M2 validation.
- The use of 220 spreadsheet values as iid observations remains unauthorized until that mapping is resolved.

Related checkpoint:
`docs/checkpoints/2026-09-21_FARIAS_AUTHOR_CLARIFICATION_PARTIAL.md`

### 6. Version hygiene

- Main EN/PT manuscripts harmonized to v0.5 pre-freeze.
- Supplementary harmonized to v1.3 pre-freeze.
- Matrix of coauthor/reviewer comments updated and re-rendered.

## Visual QA

All final DOCX artifacts in this checkpoint were rendered after their latest edits and visually inspected page-by-page.

- EN manuscript: 10 pages.
- PT manuscript: 14 pages.
- Supplementary EN: 6 pages.
- Comment-resolution matrix: 3 pages.
- Adjustment report: rendered and inspected.

No clipping, overlap, broken tables, missing glyphs, or version-header/footer errors were observed after the final corrections.

## Items intentionally still open before final scientific freeze

1. **Y3 source provenance (C-001):** formal confirmation from the C. utilis source author/coauthor, or conservative Supplementary-only treatment.
2. **C. utilis factor labels (C-002):** final author confirmation of X3/X4 mapping if not already formally documented in the coauthor round.
3. **Data-use/redistribution wording (C-004):** final authorization language from source authors.
4. **Graphical abstract terminology (C-010):** replace the final `Adding rows / Adicionar linhas` slogan with a laboratory-compatible `Synthetic data augmentation / Aumento sintético dos dados` formulation without changing the visual structure.
5. **Submission metadata (C-003/C-011):** final authors/order, affiliations, corresponding author, ORCIDs, CRediT, funding and conflict statements.

These items do not justify reopening the frozen Core or recomputing confirmatory results.

## Decision

The M2 is now a **v0.5 pre-freeze scientific candidate**. The scientific structure, external-result interpretation, terminology, figures, and literature framing are consolidated. Final scientific freeze should occur only after the remaining Y3 provenance and author/source metadata items are documented.
