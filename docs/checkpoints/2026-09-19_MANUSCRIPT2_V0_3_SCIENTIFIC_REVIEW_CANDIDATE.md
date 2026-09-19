# PEERFIX Manuscript 2 — v0.3 scientific review candidate

Date: 2026-09-19
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
Status: **PASS for coauthor scientific review; not yet journal-house-style submission version**

## 1. Governance boundary

This stage is a technical-scientific and editorial audit only. PEERFIX-Core v1.0 remains frozen. No algorithm, generator implementation, hyperparameter, seed, metric, threshold, ICD rule, downstream-model panel, adapter, confirmatory order, audit result, or scientific outcome was changed or retuned. M1 v30 remains the development manuscript. Any algorithmic redesign remains future PEERFIX-Core v1.1 sensitivity/development work.

The active editorial contract remains mandatory: short human-readable sentences; experimental/bioprocess meaning before computational jargon; specialized acronyms defined at first use; synthetic records never presented as new fermentations or biological replicates; negative findings retained; generator-specific claims kept generator-specific; relative improvements separated from absolute predictive validity; literature placed after experimental interpretation; and repository lineage/hashes preserved.

## 2. Audited source line

Input manuscript:
`Manuscript2_EN_v0_2_PEERFIX_BIOPROCESS_FOCUS_HARMONIZED.docx`

Input Supplementary:
`Supplementary_Material_Manuscript2_PEERFIX_External_Validation_EN_v1_1_HARMONIZED.docx`

Numerical authority:
- `docs/checkpoints/2026-09-17_EXT_A_C_MOGII_FINAL_AUDIT.md`
- `docs/checkpoints/2026-09-17_EXT_B_C_UTILIS_FINAL_PASS.md`
- `config/external/01_ADAPTER_C_MOGII.yaml`
- `config/external/02_ADAPTER_C_UTILIS.yaml`

## 3. Final scientific-review candidate artifacts

### Main manuscript

`Manuscript2_EN_v0_3_SCIENTIFIC_REVIEW_CANDIDATE.docx`

SHA-256:
`a45d063fdf731e7c47a92b9d62fc0dc6b4699911d03198310d24bbd4a026d712`

Rendered QA: **9 pages**, all visually inspected after the final Figure 3/source-provenance edit. No clipping, overlap, broken table, missing glyph, split caption, or unreadable figure was observed.

Narrative sentence-length audit:
- mean: approximately **12.9 words/sentence**
- median: **13**
- maximum: **25**

### Supplementary Material

`Supplementary_Material_Manuscript2_EN_v1_2_SCIENTIFIC_REVIEW_CANDIDATE.docx`

SHA-256:
`f4f2bc6dbc4b0d830e93803edf931024a4fcbb4b7c6f6208cbe98de1c70e1b98`

Rendered QA: **5 pages**, all visually inspected after final layout adjustment. Figure S3 and its caption remain together and readable. No clipping, overlap, broken table, missing glyph, or unreadable element was observed.

Narrative sentence-length audit:
- mean: approximately **11.4 words/sentence**
- median: **11**
- maximum: **22**

### Technical-scientific audit report

`Relatorio_Auditoria_Tecnico_Cientifica_M2_PreSubmissao_v1.docx`

SHA-256:
`3ef5147bc1c4f328151e0a11e4eceb6f2f541540a6edaac2cbc796f1a68f9faa`

The report records gates for Core/governance integrity, numerical consistency, cross-section coherence, provenance, figure/table interpretation, references, language/jargon control, and visual QA.

### Package

`PEERFIX_Manuscript2_Scientific_Review_Candidate_Package_v3.zip`

SHA-256:
`ebb638953863bab187e71580999b97d91a7196619eca3e3a1c01f222289ba056`

Raw author-supplied workbooks are excluded.

## 4. Main scientific audit finding — C. utilis Y3 source reconciliation

The most important audit finding was a source-provenance distinction for C. utilis Y3 (canola-oil emulsification).

The published C. utilis article describes the emulsification response models Y2/Y3 as not statistically significant/predictive in the published presentation. The author-supplied original analysis workbook, however, was preregistered in the frozen external adapter with Y3 as a **secondary domain-concordance block** carrying a conditional positive glucose × yeast-extract relation (`source_model_R2_approx: 0.321`, `source_global_p_approx: 0.0114`, `modelability_expected: CONDITIONAL_PASS`). Y2 remains the prespecified negative control (`p ≈ 0.69`) and is `BLOCKED_BY_MODELABILITY`.

This discrepancy is **not silently reconciled**. The v0.3 manuscript and Supplementary now state the source distinction explicitly. Y3 is no longer described as primary evidence of modelability. It is retained only as secondary/conditional concordance and robustness evidence because that was its preregistered role in the author-supplied workbook adapter. The revised Figure 3 labels Y3 as a secondary block and distinguishes it from the primary positive/modelable blocks.

No result was recomputed and no modelability rule was changed after observing outcomes.

## 5. Transportability/externality calibration

The title and narrative now use **selective transportability** rather than language that could imply universal or multicenter generalization.

The manuscript explicitly states that “external” means external to the PEERFIX development dataset and evaluated after Core freeze. The two validation datasets remain in the broad biosurfactant/yeast domain and share scientific collaborators/context. Therefore, M2 does not claim cross-domain, multicenter, or investigator-independent validation.

C. mogii remains the strongest positive external result, specifically for **Gaussian Copula**. TVAE transports partially; CTGAN and TabDDPM do not sustain the same predictive utility under the frozen configuration.

C. utilis Y1/Y3 retain relative improvements in selected generator/geometry combinations while absolute LR R² remains negative. Those improvements are not described as strong predictive validity.

## 6. Numerical and claim-chain audit

The Abstract, Results, Discussion, Conclusions, tables, figures, Supplementary, adapters, and audited checkpoints were cross-checked for the main numerical claims.

Examples retained from the audited evidence:
- C. mogii Gaussian Copula run-wise: TRTR R² `0.2589`, TSTR R² `0.2573`, displayed as `0.259` and `0.257`.
- C. mogii Gaussian Copula grouped-condition: TRTR R² `0.3172`, TSTR R² `0.2809`.
- C. utilis Y1 TVAE run-wise: TSTR R² `-0.1365`, displayed `-0.137`, Δ `+0.1824`.
- C. utilis Y1 TVAE grouped-condition: TSTR R² `-0.1538`, Δ `+0.4361`.
- C. utilis Y3 CTGAN grouped-condition: Δ `+0.5027`, displayed `+0.503`.
- C. utilis Y3 TVAE grouped-condition: Δ `+0.5062`.
- Y2 remains `BLOCKED_BY_MODELABILITY`; no synthetic Y2 data exist.

The C. mogii predicted-R² value previously carried in one writing line was removed from the main narrative because it is not required for the M2 claim chain and is not part of the canonical frozen adapter record used as authority here. The source-reconstruction R² and adjusted R² remain sufficient to describe the well-identified source experiment.

## 7. Language and computational-load audit

The manuscript was edited to keep short sentences and experimental meaning first. Terms such as “firewall”, “baseline”, and other process-internal/computational metaphors were reduced or replaced where a direct experimental expression was clearer. TRTR, TSTR, AUGTR, ICD, and DCR are retained only where needed and are defined before interpretive use.

The Discussion follows the active editorial sequence:
`experimental observation -> bioprocess meaning -> supporting metric -> literature`.

Computational detail necessary for reproducibility remains mainly in Methods/Supplementary rather than dominating the biological/process interpretation.

## 8. References checked in this audit

The audit verified the bibliographic identity and role of the source experiments and key methodological/bioprocess references used in M2, including:
- Silva et al., Foods 2024 — C. mogii source experiment.
- Araújo et al., Fermentation 2025 — C. utilis source experiment.
- Helleckes et al., Trends in Biotechnology 2023 — bioprocess/ML anchor.
- Lautrup et al., SynthEval, Data Mining and Knowledge Discovery 2025 — adjacent methodological support.
- Nanevski et al., PLOS Digital Health 2026 — multi-objective synthetic-data evaluation support.
- Hernandez et al., Frontiers in Digital Health 2025.
- Kaabachi et al., npj Digital Medicine 2025.
- Patki et al., DSAA 2016; Xu et al., NeurIPS 2019; Kotelnikov et al., ICML/PMLR 2023 — generator lineage/methodological provenance.

Adjacent-domain references remain subordinate to the experimental bioprocess interpretation.

## 9. Residual items — non-blocking for coauthor scientific review

Before journal submission, still resolve:
- replace the M1 placeholder citation with its real status at M2 submission;
- confirm final author list, order, affiliations, corresponding author, CRediT, funding, competing interests, and AI-use statement;
- confirm final data-availability/redistribution wording with author permissions;
- select the target journal and only then apply house style, word limits, reference style, figure limits, highlights and cover letter requirements.

These items do not reopen the frozen scientific evidence.

## 10. Decision and next stage

**PASS — SCIENTIFIC REVIEW CANDIDATE.**

The v0.3 manuscript and v1.2 Supplementary are suitable for scientific circulation among coauthors. They are not yet the journal-formatted submission version.

Next stage:
1. coauthor scientific review;
2. resolve documented scientific/editorial comments without retuning Core;
3. freeze the accepted M2 scientific text;
4. select the target journal;
5. adapt house style and assemble the final submission package.

No MLP, TabDDPM, generator, metric, threshold, seed, ICD, or other PEERFIX-Core v1.0 tuning is authorized by this checkpoint.