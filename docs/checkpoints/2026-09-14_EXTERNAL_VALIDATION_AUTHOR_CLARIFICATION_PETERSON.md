# External validation author clarification — Peterson Silva (C. mogii dataset)

Date received: 2026-09-14
Status: documentary clarification received; external confirmatory execution remains prohibited until PEERFIX-Core Gate 0.5 freeze.
Source supplied by Fernando Garcia: PDF export of e-mail reply from Peterson Felipe Ferreira da Silva.
Local source PDF SHA-256: `931675c5a26fff769fe4c6bb04f442d373f04c09a554f41108f46be90a011870`

## Clarification received

Peterson confirms that `STred` is the definitive experimental response for each run. It was the dependent variable used for the quadratic model, ANOVA, predicted values, desirability function, and optimum-condition definition. Therefore `STred` is the response that may be used in a reanalysis.

He also confirms that `STexp` was affected by a table-preparation mismatch: the publication table used laboratory execution order while Design-Expert used its randomized order. During transcription, some `STexp` measurements were associated with the wrong rows. The measured values themselves are real, but their row-level correspondence was lost in the published table. This explains why `STred = STw - STexp` does not reconcile row by row.

Peterson reports that he intends to recover the original spreadsheet and, if found, can provide:
- the design matrix in real and coded values;
- surface-tension replicates per run;
- the `STw` value used in calibration;
- the original execution order.

He does not have the native Design-Expert project file. Complementary analyses were performed in Statistica.

Regarding the proposed research use/collaboration, Peterson expressed interest but stated that he wishes to align it with Prof. Jenyffer Campos Guerra, the corresponding author and his former supervisor. This message is therefore not treated as final collaboration/authorization concurrence from all relevant authors.

## PEERFIX consequence

The previous PEERFIX external-data audit is updated as follows:

- `STred`: canonical run-level response, author-confirmed — PASS for schema/response identity.
- `STexp`: published row-level mapping invalid — EXCLUDE from model input until original correspondence is restored.
- run-level design matrix: remains usable as previously audited, subject to the published matrix and any later original-sheet reconciliation.
- raw tensiometer replicates / `STw` / original run order: pending author follow-up; if supplied, ingest only through a new provenance checkpoint before any analysis.
- no external-data outcomes may be inspected for Core tuning before Gate 0.5 final freeze.

This clarification resolves the principal `STred` versus `STexp` ambiguity without altering any PEERFIX-Core decision or threshold.
