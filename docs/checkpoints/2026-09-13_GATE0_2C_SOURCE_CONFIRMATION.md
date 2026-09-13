# PEERFIX-Core v1.0 — Gate 0.2C Source Confirmation

Date: 2026-09-13  
Status: **PASS — DERIVATION DATASET SOURCE CONFIRMED**

## Scope
Gate 0.2B recovered the manuscript-lineage PEERFIX2 dataset but initially left its original public source unresolved. A direct source check has now identified and reconciled all 20 rows against the original open-access experimental document.

## Primary source
**Souza, Fabiana América Silva Dantas de. _Biodegradação de óleo diesel por Candida lipolytica em água do mar_. 2009. 175 f. Dissertação (Mestrado em Desenvolvimento de Processos Ambientais), Universidade Católica de Pernambuco, Recife. Defense date: 15 April 2009.**

Institutional/Brazilian Digital Library metadata identify the work as a 2009 open-access master's dissertation, not a 2015 doctoral thesis at UFPE.

The experimental document reports three full factorial designs. PEERFIX2 uses **Planning 2**, described as a full `2^4` design with 20 assays including four center-point replicates, evaluating seawater, urea, ammonium sulfate and monobasic potassium phosphate against emulsification activity and surface tension after 168 h.

## Exact source tables
### Table 4 — factor levels (original document p. 130)
The source defines Planning 2 levels as:

| Factor | -1 | 0 | +1 |
|---|---:|---:|---:|
| Seawater (% v/v) | 0 | 50 | 100 |
| Urea (% w/v) | 0 | 0.25 | 0.5 |
| Ammonium sulfate (% w/v) | 0.2 | 0.4 | 0.6 |
| KH2PO4 (% w/v) | 0.5 | 1.0 | 1.5 |

These are exactly the PEERFIX2 factor levels.

### Table 8 — 20-run Planning 2 matrix and surface tension (original document p. 134)
The original Table 8 contains the following surface-tension values, in the exact run order used by the recovered manuscript-lineage dataset:

`45.05, 46.47, 53.30, 53.57, 52.27, 53.24, 50.58, 46.67, 47.54, 43.76, 47.61, 47.58, 42.35, 50.98, 42.22, 48.44, 49.44, 44.26, 47.75, 49.21` mN/m.

The four center-point observations are runs 17–20:

`49.44, 44.26, 47.75, 49.21` mN/m.

All factor combinations and all 20 surface-tension values match `data/derivation/peerfix2_historical_manuscript_dataset.csv` exactly.

## Dataset identity
Canonical derivation candidate:

`data/derivation/peerfix2_historical_manuscript_dataset.csv`

SHA-256, exact UTF-8 CSV bytes including final newline:

`c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

Result: **20/20 row-level source match**.

## Scientific fingerprint
The source-confirmed dataset also reproduces the manuscript-lineage coded-factorial coefficients:

- KH2PO4 main effect: coefficient `-1.916875`, p = `0.0301776`;
- urea × ammonium-sulfate interaction: coefficient `-1.885625`, p = `0.0323252` under the PEERFIX coded refit.

The first term is consistent with the original source's sparse surface-tension effect interpretation. The second remains a PEERFIX candidate/borderline relation because the original experimental interpretation did not classify it as significant.

## Important bibliography correction
The current late-stage PEERFIX2 manuscript cites:

`Souza, F. A. S. D. (2015). Biodegradation of diesel oil by Candida lipolytica in seawater [Doctoral thesis, Universidade Federal de Pernambuco].`

That record is not the source now verified for these 20 observations. The source-confirmed bibliographic record is the **2009 master's dissertation at Universidade Católica de Pernambuco**.

Therefore, before manuscript submission, all occurrences of `Souza, 2015` referring to this experiment and the corresponding reference-list entry must be corrected to the verified 2009 source unless a separate 2015 publication containing the same table is independently documented.

This is a bibliographic/provenance correction; it does not change the recovered experimental values.

## Dataset B status
The alternative 20-row dataset introduced during cleanup commit `6161c35...` remains quarantined at:

`data/quarantine/cleanup_substituted_dataset_6161c35.csv`

Its provenance has not been established and its effect structure is inconsistent with the PEERFIX2 manuscript. It is excluded from derivation and confirmatory processing.

## Gate decision
**PASS for derivation-data source traceability.**

The prior Gate 0.2B temporary block on source identity is lifted for Dataset A.

Real derivation execution is still not authorized until the pre-freeze protocol is revised to point to the source-confirmed dataset and Gate 0.3 environment/generator integration tests are complete.

## Next action
Issue `PEERFIX_CORE_v1.0_PRE_FREEZE_REV1.yaml` with:

- derivation path changed to `data/derivation/peerfix2_historical_manuscript_dataset.csv`;
- SHA-256 changed to `c33869...`;
- source traceability = pass;
- source = Souza 2009, UNICAP, Planning 2, Tables 4 and 8;
- Dataset B explicitly prohibited;
- Gate 0.2C recorded as passed.
