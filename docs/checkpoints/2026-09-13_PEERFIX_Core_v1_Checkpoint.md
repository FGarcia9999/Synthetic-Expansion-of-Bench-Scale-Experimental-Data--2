# PEERFIX-Core v1.0 — Scientific Freeze Preparation — Checkpoint 2026-09-13

## Purpose
Preserve a reproducible recovery point before the formal freeze of PEERFIX-Core v1.0 and before any confirmatory execution on external datasets.

## Repository baseline
- Base branch used for this checkpoint: `cce-v26-zenodo-metadata`
- Base commit observed before branching: `6161c35bfe18d17d87b2b23750334e13b44749e8`
- Checkpoint branch: `checkpoint/peerfix-core-v1-freeze-2026-09-13`
- `main` commit referenced by the current manuscript lineage: `4ac9fdf8585a4592d7214aa99df1b5fffc07fa1d`

## Scientific program status
- **M1 / PEERFIX2:** derivation/development study; immediate priority.
- **Former PEERFIX3 / Yali:** removed as confirmatory external-validation dataset because the required granular observations cannot be recovered.
- **Candida mogii (Foods 2024):** strong external candidate; 27 explicit CCRD runs; pending author clarification of `STexp` versus `STred`.
- **Candida utilis (Fermentation 2025):** strong external candidate; 19 explicit runs and three responses; pending author confirmation of the physical identity of `X3` and `X4`.
- **Farias et al. (2021):** six supplementary XLSX files audited cell by cell; pending clarification of the experimental meaning and independence of `SAMPLES 1–5`.
- **PEERFIX4 / Ivison:** retained as provenance/modelability stress-validation study, conditional on reconciliation with the original researchers.

## Governance rule
No external dataset will be used for confirmatory execution before the Core is frozen. Findings from M2 or M3 must not retroactively change PEERFIX-Core v1.0. Any scientifically justified later change must be versioned as a new Core release.

## Current PEERFIX2 invariants supported by the manuscript
- Real derivation dataset: full `2^4` factorial design with center-point replicates, `n = 20`.
- Primary response: surface tension.
- Four generator families: Gaussian Copula, CTGAN, TVAE, TabDDPM.
- Leakage-free principle: each generator is fitted only to the real training fold.
- TSTR and TRTR use the same held-out real observations and the same downstream model.
- TSTR, TRTR and Delta are reported separately.
- Domain concordance is evaluated independently from predictive utility.
- ICD uses sign, magnitude and detectability plus a penalty for spurious terms.
- DCR is a proximity diagnostic, not a privacy certificate.
- Synthetic observations are an auditable computational complement and are never treated as new experimental replication.

## Gate 0 blockers before formal freeze
### 1. Repeated-k-fold lineage
The final manuscript states `5 folds x 5 repetitions x 2 scenarios`, i.e. 50 fold-refit utility fits per generator. A preserved historical `run_metadata.json` records `n_splits = 5` and `n_repeats = 10`.

**Required action:** identify the exact code/config/output set that produced the final manuscript tables and figures, then regenerate a single canonical execution manifest.

### 2. Authorship and repository governance
Historical README/Zenodo metadata still reflect a previous author/creator configuration.

**Required action:** harmonize manuscript, CRediT, README, CITATION.cff, Zenodo metadata and release metadata before submission. Authorship of the new computational work must reflect qualifying contributions to the new study, while the original experimental source remains explicitly cited and credited.

### 3. Licensing boundaries
The historical repository broadly assigns CC BY 4.0 to data, figures, tables and documents.

**Required action:** separate clearly:
- original experimental observations and their source/license;
- canonical/transcribed PEERFIX dataset and provenance record;
- new software/code license;
- new manuscript, figures and tables.
Do not re-license the original experimental data unless the original source explicitly permits it.

## Scientific items to freeze explicitly
1. Confirmed KH2PO4 main effect = primary domain ground truth.
2. Urea x ammonium-sulfate interaction = candidate/borderline secondary effect, with lower interpretive weight.
3. ICD magnitude tolerance bands.
4. ICD penalty `lambda` and sensitivity policy.
5. Generator hyperparameters and seed policy.
6. Final repeated-k-fold scheme and uncertainty calculation.
7. Downstream-model selection rule `m*` to avoid optimistic selection.
8. Exact boundary between invariant PEERFIX-Core components and dataset-specific adapters.

## Manuscript PT v29 received at this checkpoint
File supplied in the project workspace: `manuscrito_PT_v29_CCE.docx`.

SHA-256:
`576bb1cd4aa6fc4ce15d140e95e758dd8b3877cfb59e580ef5749aca01281df1`

**Do not promote v29 as canonical yet.** Its abstract mentions `Candida guilliermondii UCP 1592`, whereas keywords, introduction, dataset description and results remain based on `Candida lipolytica UCP 988`. This must be reconciled before any manuscript freeze.

## Audit-artifact hashes preserved outside GitHub at this checkpoint
- `PEERFIX_Core_v1_Gate0_Checkpoint01.md` — `929398d6db69fe4f6c9eadec38250371eaa5cf068faf669c097379d74c019ed5`
- `PEERFIX_EXT1_Farias_Auditoria_celula_a_celula_v1.xlsx` — `05334d47091a4702140bb1043c13f3556dce32a1c77259763caf8953c86101b0`
- `PEERFIX_EXT1_Farias_Relatorio_Auditoria_v1.md` — `4c60d59b4c1c0d8b825b84a594967636ea0330346715bb8aa00d39b9ffb5ef0e`
- `PEERFIX_EXT1_Auditoria_Elegibilidade_Mogii_Utilis_v1.xlsx` — `2771a563a1e6cc34e1ab9f9ad8ab7f068c7e48e881a9e5d6c220cb14ea6c5f82`
- `PEERFIX_EXT1_Relatorio_Auditoria_Mogii_Utilis_v1.md` — `49542a39e00b1324f7c09d67e741a93c9acd371e440af19717d1be8bc34ee578`

## Next authorized gate
**Gate 0.1 — Reproducibility lineage**

Tasks:
- identify the exact code/config/output set underlying the final PEERFIX2 manuscript;
- reconcile `5 vs 10` utility repetitions;
- map manuscript tables and figures to exact output files and hashes;
- establish one canonical execution manifest;
- only after PASS create `PEERFIX_CORE_v1.0_FROZEN.yaml`.
