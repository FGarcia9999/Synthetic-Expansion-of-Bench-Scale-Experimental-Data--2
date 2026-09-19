# PEERFIX Manuscript 2 — coauthor circulation package

Date: 2026-09-19
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
Parent scientific-review checkpoint: `b98c8183bb2e56c60a5aca1b8525475eb3bc77eb`
Status: **ready for coauthor circulation; scientific freeze not yet declared**

## 1. Governance boundary

This checkpoint prepares the coauthor-review stage only. PEERFIX-Core v1.0 remains frozen. No algorithm, generator implementation, hyperparameter, seed, metric, threshold, ICD rule, model panel, adapter, confirmatory order, audit result, or scientific outcome was changed or retuned.

The scientific master remains:
- `Manuscript2_EN_v0_3_SCIENTIFIC_REVIEW_CANDIDATE.docx`
- `Supplementary_Material_Manuscript2_EN_v1_2_SCIENTIFIC_REVIEW_CANDIDATE.docx`

The circulation copies are protected for **comments-only review**. Reviewers are asked to propose wording inside comments instead of directly changing numbers, tables, figures, or frozen results.

## 2. Circulation artifacts

### Main manuscript review copy
`Manuscript2_EN_v0_3_COAUTHOR_REVIEW_COMMENT_ONLY.docx`

SHA-256:
`c70034f7bb8a7a36b9138b7ccca196ee3ec811529f9b270a5582575311f11e51`

Protection state: Word document protection `edit=comments`, `enforcement=1`.

Visual QA: 9 pages. Pixel comparison against the already approved scientific-review master render showed all 9 pages identical.

### Supplementary review copy
`Supplementary_Material_Manuscript2_EN_v1_2_COAUTHOR_REVIEW_COMMENT_ONLY.docx`

SHA-256:
`b5757354c402b53ff472c9dbdc8a322f8f7e94912b1130aacfc8edf529fd3360`

Protection state: Word document protection `edit=comments`, `enforcement=1`.

Visual QA: 5 pages. Pixel comparison against the already approved scientific-review Supplementary render showed all 5 pages identical.

### Review guide
`Guia_Revisao_Coautores_M2_v0_3.docx`

SHA-256:
`9fe5b5b5cbdf8c6b41d3ec85b9be7e147e725d07a7ff849985eeb8b5a9fd25ce`

The guide defines what remains frozen, what reviewers should examine, how to register comments, which confirmations are mandatory, and the gate for final scientific freeze.

### Comment-resolution matrix
`Matriz_Resolucao_Comentarios_M2_v0_3.docx`

SHA-256:
`6e00f6503ff690ad5f10d104b80227ea2d51a3f52eb96593371007f8087f8c3d`

The matrix starts with five open governance/scientific items and leaves additional rows for coauthor comments.

### Circulation message
`Mensagem_Circulacao_Coautores_M2_v0_3.docx`

SHA-256:
`a7306402993ea9c7d6014673905ab25d45a1164d69533a4bc069ce482e722435`

The message is ready to send after the return date is filled in.

### Audit report included for reference
`Relatorio_Auditoria_Tecnico_Cientifica_M2_PreSubmissao_v1.docx`

SHA-256:
`3ef5147bc1c4f328151e0a11e4eceb6f2f541540a6edaac2cbc796f1a68f9faa`

## 3. Coauthor confirmation items opened before freeze

- **C-001 — C. utilis Y3 provenance/role.** Confirm the distinction between the published article and the author-supplied workbook, and confirm that Y3 is retained only as a secondary/conditional concordance block rather than primary modelability evidence.
- **C-002 — C. utilis factor mapping.** Confirm `X3 = yeast extract` and `X4 = ammonium nitrate` and that the textual inversion does not alter the experimental matrix or numerical models.
- **C-003 — authorship and affiliation.** Confirm final author list, order, affiliations, corresponding author, and later CRediT roles.
- **C-004 — data-use/redistribution statement.** Confirm analysis authorization and the limits on public redistribution of the original workbooks.
- **C-005 — Farias et al.** Keep outside the required evidence chain unless measurement independence is formally clarified.

## 4. Scientific-freeze gate

The definitive M2 scientific freeze must not be declared until:

1. all scientific comments are classified and resolved;
2. C-001 to C-004 are confirmed or have a documented final decision;
3. Abstract, Results, Discussion and Conclusions remain consistent with the same audited confirmatory results;
4. no accepted comment requires recomputation, generator retuning, threshold changes, new seed selection, or any retroactive modification of PEERFIX-Core v1.0.

Any proposal requiring new processing belongs to a future PEERFIX-Core v1.1 development/sensitivity line rather than being folded into v1.0 post hoc.

## 5. Coauthor circulation package

`PEERFIX_M2_v0_3_Pacote_Circulacao_Coautores_v1.zip`

SHA-256:
`2e1847ec64b28d214fe4c2e7e82a042c7c92a40c6af1c9c4c7b9c2cdc4c33020`

The package contains the two comments-only review copies, review guide, comment-resolution matrix, ready-to-send circulation message, technical-scientific audit report, README, and SHA-256 manifest. Raw author-supplied workbooks are excluded.

## 6. Next stage

The next stage is **receipt and documented resolution of coauthor comments**. Only after that resolution should a definitive M2 scientific freeze be recorded. Journal selection and house-style adaptation remain downstream steps and do not start during the comment-collection phase.

## Decision

**PASS — coauthor circulation package prepared and repository lineage recorded.** Scientific content remains the v0.3 review candidate; the package adds review governance only.