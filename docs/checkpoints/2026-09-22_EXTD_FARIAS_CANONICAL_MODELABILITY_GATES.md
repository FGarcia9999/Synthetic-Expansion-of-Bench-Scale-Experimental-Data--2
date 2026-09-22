# PEERFIX EXT-D — Farias canonicalization and pre-generation modelability gates

Date: 2026-09-22
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## Scope

This checkpoint records a **pre-generation eligibility audit only** for the Farias et al. (2021) dataset. No synthetic generation was executed. No PEERFIX-Core file, generator, seed, threshold, metric, ICD rule, downstream model or hyperparameter was changed.

## Critical source reconciliation

The six public supplementary XLSX workbooks contain 44 condition–response groups and five numeric rows labelled `SAMPLES 1–5` inside every group. The workbooks explicitly calculate `AVERAGE` and `STDEV` over those five numeric rows. The published article, however, states that Figures 2–6 show averages of triplicate experiments. Direct author correspondence later stated that `SAMPLE 1–5` should not be interpreted as independent fermentations, repeated readings, or triplicate means and described them as experimental variations of carbon source/cultivation conditions.

These statements do not map cleanly onto the workbook layout because medium, temperature, strain and assay condition are already fixed outside the `SAMPLE 1–5` rows. Therefore the row-level biological semantics remain internally inconsistent across the documentary layers.

**Conservative decision:** do not promote the five numeric rows to independent experimental units. Preserve them for audit only. The canonical inferential unit is the workbook/article **condition-level summary** (one row per organism × production medium × temperature × assay factor). This supersedes any earlier interpretation that `SAMPLE 1–5` themselves could be used as five independent treatment units.

## Canonical matrix

The condition-level matrix contains:

- 32 surface-tension conditions;
- 6 emulsification (E24) conditions;
- 6 motor-oil-dispersion conditions.

Source workbooks and hashes remain those frozen in the prior cell-level audit. For s001–s005 the workbook summary formulas reconcile exactly with the five stored numbers. For s006, hardcoded summary values remain non-canonical; recalculated values from the stored numbers are preserved in the audit, and the discrepancy remains logged.

## Modelability / identifiability gate

Only source-data modelability was evaluated. The minimal model for each biological block was defined from the experimental structure in Table 1 before synthetic generation:

- `P. cepacia` surface tension: medium + temperature;
- `P. aeruginosa UCP0992` surface tension: medium + temperature;
- ATCC10145 + ATCC9027 surface tension: strain + medium + temperature;
- strain-specific ATCC surface-tension checks: medium + temperature;
- E24: strain + oil;
- motor-oil dispersion: strain + biosurfactant:oil ratio.

The primary source-modelability criterion is support for a global factor–response relationship at the 95% significance level, consistent with the source article's statistical convention and the modelability logic already used in PEERFIX external validation. Adjusted R², leave-one-condition-out R² and a 20,000-permutation response test (fixed seed 20260922) are robustness diagnostics only and do not modify Core thresholds.

## Results

| Block | n conditions | Global p | Adjusted R² | LOO R² | Permutation p | Gate |
|---|---:|---:|---:|---:|---:|---|
| P. cepacia surface tension | 10 | 0.0460 | 0.7559 | 0.3221 | ~0.053 | `CONDITIONAL_PASS` |
| P. aeruginosa UCP0992 surface tension | 10 | 0.00581 | 0.9165 | 0.7679 | ~0.010 | `PASS_MODELABILITY` |
| ATCC10145 + ATCC9027 surface tension | 12 | 0.01345 | 0.6867 | 0.4141 | ~0.023 | `PASS_MODELABILITY` (supporting combined view) |
| P. aeruginosa ATCC10145 surface tension | 6 | 0.00354 | 0.9941 | 0.9788 | ~0.016 | `PASS_MODELABILITY` |
| P. aeruginosa ATCC9027 surface tension | 6 | 0.07399 | 0.8751 | 0.5504 | ~0.087 | `CONDITIONAL` |
| E24, two ATCC strains | 6 | 0.8692 | -0.8558 | -5.6811 | ~0.966 | `BLOCKED_BY_MODELABILITY` |
| Motor-oil dispersion, two ATCC strains | 6 | 0.1919 | 0.6690 | -0.1915 | ~0.113 | `BLOCKED_BY_MODELABILITY` |

## Scientific interpretation

### Preferred prospective EXT-D block

`P. aeruginosa UCP0992` surface tension is the cleanest primary candidate. It provides five production media crossed with two temperatures while pH, agitation and fermentation time remain fixed. Both medium and temperature show supported contributions in the additive condition-level model, and leave-one-condition-out performance remains positive.

### Strong secondary block

`P. aeruginosa ATCC10145` surface tension is also eligible and shows a strong condition-level relationship. It is retained as a distinct biological block rather than being silently pooled with ATCC9027.

### Conditional blocks

`P. cepacia` remains conditional because the historical canola-oil/corn-steep-liquor condition was fermented for 60 h at 250 rpm, whereas the remaining media used 96 h at 200 rpm. The statistical relationship is borderline robust and its medium effect cannot be interpreted causally apart from process settings.

ATCC9027 surface tension remains borderline: apparent fit is high, but the global relationship does not cross the 95% significance criterion at n=6. It remains part of the evidence ledger and is not deleted.

### Fail-closed blocks

E24 and motor-oil dispersion do not support a sufficiently stable global relationship for synthetic generation under this audit. They remain scientific negative controls / descriptive evidence and are **not** to be rescued by alternate models, threshold changes or generator tuning.

## Prospective execution decision

No synthetic generation is authorized by this checkpoint. After the M2 scientific freeze, a dedicated EXT-D execution checkpoint may authorize the frozen PEERFIX-Core v1.0 on the eligible blocks. All blocked and conditional outcomes must remain visible; no post-outcome dataset or response substitution is allowed.

## Artifact

Canonical/modelability workbook:
`PEERFIX_EXTD_Farias_Canonical_Modelability_Gates_v1_2026-09-22.xlsx`

SHA-256:
`37984d99ff045b8a06bc289013c5f44c4eef6b88cf9358cb468d2bd9e5fdc0fa`
