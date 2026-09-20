# PEERFIX Manuscript 2 — journal-neutral submission package

Date: 2026-09-19
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
Status: **submission-preparation support only; no journal selected; no scientific freeze declared in this step**

## Governance boundary

This checkpoint records journal-neutral submission materials prepared from the current M2 scientific line. PEERFIX-Core v1.0 remains frozen. No generator, hyperparameter, seed, threshold, metric, ICD rule, adapter, model panel, confirmatory result, or decision rule was altered or retuned.

The package preserves the active editorial contract: short human-readable sentences; experimental/bioprocess meaning before computational jargon; specialized terms only where necessary; synthetic rows never described as new fermentations or biological replicates; unfavorable findings retained; generator-specific claims kept generator-specific; relative improvement separated from absolute predictive validity; and the C. utilis Y3 provenance distinction kept open for explicit coauthor confirmation.

## Source basis

The submission-facing text was grounded in the current M2 manuscript line and its frozen interpretation, including:

- two external biosurfactant datasets not used in PEERFIX development;
- C. mogii: 27-run central composite design, strongest positive external result with Gaussian Copula;
- C. utilis: 19-run factorial design with Y1/Y3 relative improvements but negative absolute R²;
- C. utilis Y2: blocked before generation because source modelability was unsupported;
- public traceability via SHA-256 hashes, adapters, protocol definitions and derived results, without assuming permission to redistribute original workbooks.

## Artifacts

### English journal-neutral submission package

`PEERFIX_M2_Journal_Neutral_Submission_Package_EN_v1.docx`

SHA-256:
`34cce7ae42feebfb13fffa1de5b01a1cecb8a5f655f883bb91e84fd0bee502ed`

Contents:
- manuscript identity;
- two cover-letter variants: biochemical/process-engineering emphasis and computational/process-modeling emphasis;
- proposed highlights;
- graphical-abstract technical brief;
- CRediT confirmation template;
- funding working options;
- competing-interest working statement;
- data-availability/traceability base;
- acknowledgments template;
- ethics/consent note for journal forms;
- explicit list of metadata that must remain open until coauthor confirmation.

Rendered QA: **5 pages**, all visually inspected. No clipping, overlap, broken table, missing glyph, or orphaned table header was observed.

### Portuguese journal-neutral submission package

`PEERFIX_M2_Pacote_Submissao_Neutro_PT_v1.docx`

SHA-256:
`5aa262e250df52bd6d825d6589e334e056f4ad1292c5d66cffa9e5b59f16f53d`

This is the Portuguese coauthor-readable counterpart of the English package. It keeps the same scientific caution and submission placeholders.

Rendered QA: **5 pages**, all visually inspected. No clipping, overlap, broken table, missing glyph, or unreadable element was observed.

### Bilingual coauthor metadata / CRediT confirmation form

`PEERFIX_M2_Coauthor_Metadata_CRediT_Confirmation_Form_v1.docx`

SHA-256:
`36c2b618fc5f6da5939aaec967af8692d58d0f8990a62b59706a7977f1a1819a`

The form requests explicit confirmation of:
- final author order;
- affiliations;
- corresponding author;
- email/ORCID;
- individual CRediT roles;
- funding;
- competing interests;
- acknowledgments;
- raw-data redistribution limits;
- final C. utilis Y3 wording.

Rendered QA: **2 pages**, visually inspected.

### Package ZIP

`PEERFIX_M2_Journal_Neutral_Submission_Package_v1.zip`

SHA-256:
`cf6af4dc142c18de8303ceb22b46aa994622f1295cb2cdf659856fb5323475b8`

The ZIP contains the EN package, PT package, bilingual confirmation form, SHA-256 manifest and README.

## Items intentionally not inferred

The current manuscript does not supply enough information to finalize the following items, so this package does not invent them:

1. final author list/order beyond the currently named authors;
2. final affiliations;
3. final corresponding author;
4. individual CRediT roles;
5. funding agency/grant data;
6. final competing-interest declaration;
7. acknowledgments;
8. permission for broader redistribution of the original workbooks.

Standard wording is supplied only as a working option and is explicitly marked as requiring confirmation before submission.

## Graphical abstract direction

The proposed graphical abstract remains a technical brief, not a finalized figure. Its intended flow is:

`small real experiments -> frozen PEERFIX-Core v1.0 -> held-out-real validation -> selective outcomes -> return to bench confirmation`

Outcome classes:
- positive selective transportability: C. mogii / Gaussian Copula;
- relative gain only: C. utilis Y1/Y3, while absolute R² remains negative;
- blocked before generation: C. utilis Y2.

Final process message:
`synthetic rows are not new fermentations` and `synthetic expansion supports exploration, while new bench runs provide confirmation`.

## Decision

**PASS — journal-neutral submission-support materials prepared and visually QA-checked.** The project can continue without waiting for minor coauthor wording comments. Those comments can later be incorporated into the manuscript and these submission materials through the existing controlled comment-resolution workflow. Journal selection and journal-specific house-style adaptation remain downstream steps.