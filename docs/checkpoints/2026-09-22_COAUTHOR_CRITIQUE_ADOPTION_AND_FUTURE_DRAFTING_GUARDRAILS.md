# PEERFIX program — adoption of coauthor critique and future drafting guardrails

Date: 2026-09-22
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## Purpose

This checkpoint records the technical decisions adopted after review of the coauthor's two documents dated 2026-09-22 and the subsequent technical reconciliation. It is a **decision ledger / drafting charter**, not manuscript prose.

The material is intentionally stored as concepts, gates, constraints, trigger conditions and editorial boundaries. **No paragraph from the coauthor review documents, from the current M1/M2 drafts, or from this checkpoint is to be copied verbatim into a future manuscript.** Any future M3 text must be written from a blank outline using the scientific decisions below, with fresh wording and manuscript-specific argumentation. This is intended to reduce textual overlap / self-reuse risk and to preserve the distinct scientific question of each manuscript.

## Source review artifacts preserved

1. `PEERFIX_Gates_Representabilidade_Matriz_RegraTransporte.docx`
   - SHA-256: `4a13b731da1f26863d6e74d511d1b3219e631a1f197a576fe72bdfda13e9f0f4`
2. `Parecer_EXTC_EXTD_e_sugestoes_Core.docx`
   - SHA-256: `0e53a6dd8e7424cc072a240e3d3bfc6c1ceb60d7abeb18a1e3998de0ab1250d1`

These files are evidence of the review process. Their wording is **not** a manuscript text source.

## Adopted program-level decisions

### A. Manuscript 1 — development paper

- Scientific identity remains unchanged: development and freezing of PEERFIX-Core v1.0 on the derivation experiment.
- EXT-A/B/C/D results are not development evidence and may not be used to recalibrate or strengthen the original development claims.
- A future M1 maintenance version may update only the temporal/status wording of post-freeze scenarios (for example, replacing outdated statements that Fontes/Farias were still unexecuted).
- No post-freeze numerical result should be imported into M1 Results/Discussion as development evidence.

### B. Manuscript 2 — external-validation paper

- Scientific interpretation remains frozen under `2026-09-22_MANUSCRIPT2_SCIENTIFIC_FREEZE.md`.
- Confirmatory chain remains limited to `C. mogii` and `C. utilis`.
- Fontes EXT-C and Farias EXT-D remain outside M2 confirmatory evidence.
- Y3 remains Supplementary-only / conditional robustness evidence; it is not reopened.
- Only submission/editorial metadata and wording clean-up that does not change scientific meaning may proceed.
- Historical wording about Farias may be shortened to state that it was reserved for a separately preregistered post-M2 route; no post-freeze outcome is imported.

### C. Manuscript 3 — future fail-closed / decision-gate paper

M3 should be **rewritten from scratch** around a broader scientific question than the earlier 'modelability structural' concept:

> Can a frozen synthetic-data protocol distinguish experiments that should proceed from those that should be restricted or refused before synthetic generation?

The future M3 should not re-demonstrate the M1 dissociation thesis and should not re-run the M2 external-validation narrative. Its own contribution is the **decision architecture and boundary conditions** of a frozen protocol.

## Future gate architecture for M3

The 2x2 modelability × representability matrix is adopted as an important visual/conceptual device, but it is **not exhaustive of the whole protocol**. It applies only after a provenance/experimental-unit gate has passed.

Recommended gate sequence:

1. **G0 — Provenance / experimental unit / structural integrity**
   - source traceability;
   - experimental unit identifiable;
   - no unsupported pseudoreplication;
   - labels/units/hierarchy sufficiently reconstructible for inference.
   - failure status should be recorded explicitly (e.g., `BLOCKED_BY_PROVENANCE_OR_UNIT`).

2. **G1 — Modelability / identifiability**
   - the source experiment must support the factor-response relation needed for synthetic expansion.
   - failure: `BLOCKED_BY_MODELABILITY`.

3. **G2 — Representability**
   - all required factors **and their joint feasibility constraints** must be encodable in the frozen Core without artificial ordering, impossible combinations, or a different experimental geometry.
   - this is broader than 'categorical factors only'. It also covers constrained mixtures, conditional factors, joint-support restrictions, hierarchical designs and other structures that the frozen representation cannot preserve.
   - failure: `BLOCKED_BY_REPRESENTABILITY` (or the already logged `BLOCKED_BY_ADAPTER_REPRESENTABILITY`; terminology should be harmonized once, before drafting M3).

4. **G3 — Frozen execution / integrity**
   - no outcome-driven retuning;
   - all generators and geometries retained;
   - audit trail must pass.

Only after G0–G3 pass does the protocol evaluate predictive transport, concordance/fidelity and proximity diagnostics.

## Farias EXT-D — adopted interpretation

- Condition-level canonicalization remains the safe inferential level.
- `R1–R5 / SAMPLE 1–5` are preserved for audit but are **not** promoted to independent experimental units.
- The exact biological meaning of the five within-condition values should not be asserted beyond what the source documentation supports.
- UCP0992 and ATCC10145 may pass modelability while still failing representability in PEERFIX-Core v1.0 because the production-medium factor is nominal/formulation-based and cannot be encoded neutrally by the frozen numeric generation interface.
- Final state should therefore be expressed as:
  - `modelability = PASS`
  - `representability = FAIL`
  - `generation = BLOCKED`
- This is a positive fail-closed behavior of the protocol, not a biological failure of the source experiment.

## Fontes EXT-C — adopted role

- EXT-C remains a prospective post-freeze execution under the frozen Core.
- It provides the positive/executable contrast needed by the future M3.
- EI + TVAE: selective positive predictive transport under the frozen analysis.
- delta-ST + TVAE: positive absolute predictive signal with systematic loss versus real-data reference; retain as partial transport.
- Structural concordance and predictive transport remain separate objectives; no generator is globally superior.
- Fontes should not be used to retrospectively strengthen M2.

## Predictive-transport rule — what is and is not adopted

The coauthor proposal (`mean TSTR R2 > 0`, >=8/10 positive repeats, and delta tolerance such as 0.10) is **not adopted as a retrospective confirmatory criterion for C. mogii or Fontes**, because it was articulated after those outcomes were observed.

Adopted governance:

- For already completed C. mogii/Fontes analyses, such a rule may be shown only as a **retrospective descriptive/sensitivity classification**, clearly labelled post-outcome.
- A future primary transport decision rule must be fixed prospectively **before the next new external execution**.
- Any numeric tolerance (e.g., delta = 0.10) requires independent methodological justification; it may not be justified merely because it reproduces existing desired classifications.
- Prefer separating two concepts:
  1. **predictive transport retained**: synthetic-only training retains positive predictive signal on held-out real experimental data with prespecified stability;
  2. **near-reference transport**: predictive transport retained and TSTR remains within a preregistered tolerance of TRTR.
- `partial` should be used only under a prospectively defined rule, not retrofitted to create a favorable ordering.

## Uncertainty reporting

- The need to report uncertainty/stability around small positive TSTR values is adopted.
- Do not treat the 10 repeated-CV repeats as 10 independent experiments.
- Immediate descriptive reporting should include median/IQR/range and fraction of repeats with positive TSTR.
- If an inferential interval is added, prefer a unit/condition-aware resampling strategy (e.g., clustered bootstrap over experimental units/conditions while preserving prediction dependence) rather than an naive bootstrap of the 10 repeat means.
- Any future interval procedure must be specified before new confirmatory execution if it is used for classification.

## Protocol-sequence deviation

The original prospective plan mentioned EXT-C/EXT-D execution after M2 freeze and submission. EXT-C was executed after the scientific freeze but before formal journal submission.

Adopted treatment:

- Do **not** create a retroactive preregistration amendment pretending that pre-submission execution had been prospectively authorized.
- Record this transparently as a **sequence deviation**:
  - M2 scientific freeze occurred before EXT-C execution;
  - formal journal submission had not yet occurred;
  - no M2 scientific claim, Core setting, generator, seed, threshold, metric or decision rule was changed between freeze and EXT-C execution;
  - EXT-C remains outside the M2 evidence chain.

## Higher-order hypothesis for future M3

The idea that source-design information governs transportability is retained as a **testable hypothesis**, not a current conclusion.

Preferred formulation:

> The experimental information contained in the source design constrains the possibility of predictive transport, while the realized transport remains response- and generator-dependent.

Do not claim that source design is more important than generator family based on the current small number of heterogeneous experiments.

Also, do not describe Fontes EXT-C as an RSM/CCD case: the preregistered EXT-C primary dataset is the Table 4 full `2^4` factorial plus three center-point assays; the later CCD/RSM is not the primary EXT-C dataset.

## Anti-overlap / fresh-drafting rule

When M3 drafting is authorized:

- start from a blank outline;
- write every section anew;
- use this checkpoint only as a decision ledger;
- do not copy prose from M1, M2, coauthor reviews, cover letters, prior reviewer reports or preregistration text;
- shared method facts should be stated minimally and, where possible, cross-referenced to M1 rather than re-explained at length;
- figures/tables may reuse underlying results only when scientifically necessary, but captions, framing and interpretation must be newly written for the M3 question;
- retain a manuscript-level overlap audit before submission.

## Trigger conditions for future application

### M1 maintenance update may start when
- coauthor scientific comments on M1 are consolidated;
- authorship/CRediT metadata are sufficiently stable.

### M2 submission formatting may start when
- coauthor review of the frozen interpretation is closed;
- authorship/order/affiliations/CRediT/funding/conflict/data-use text are resolved.

### M3 full drafting may start when
- the program explicitly chooses the M3 scope as fail-closed decision architecture / protocol boundaries;
- the adopted G0–G3 terminology is frozen;
- the treatment of Farias representability is harmonized in all ledgers;
- the retrospective/prospective status of the transport rule is clearly separated;
- no additional external execution needed for M3 is started before any new classification rule is preregistered.

## Status

**ADOPTED AS FUTURE GOVERNANCE / DRAFTING CHARTER.**

This checkpoint does not modify PEERFIX-Core v1.0 and does not reopen M1/M2 scientific results. It preserves the coauthor's useful conceptual contribution while adding the technical restrictions needed for prospective, auditable use at the appropriate manuscript stage.