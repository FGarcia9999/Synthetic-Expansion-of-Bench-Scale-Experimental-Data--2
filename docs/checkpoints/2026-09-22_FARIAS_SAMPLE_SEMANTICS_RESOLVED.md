# PEERFIX — Farias SAMPLE 1–5 semantics resolved

Date: 2026-09-22
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## Author clarification

Charles Farias explicitly clarified that `SAMPLE 1–5` do **not** correspond to independent replicate fermentations, repeated analytical readings, or means of five repeated measurements. They represent experimental variations/levels of carbon sources and cultivation conditions selected from the literature and prior experimental knowledge.

This resolves the principal semantic ambiguity that remained in the Farias supplementary XLSX files.

## Consequence for experimental hierarchy

- `SAMPLE 1–5` must be encoded as **treatment/design levels**, not as biological replicates.
- The triplicate fermentations described in the article are a distinct experimental layer and must not be reconstructed from `SAMPLE 1–5`.
- If the triplicate-level values are not individually present in the public workbooks, the safe observational unit is the reported experimental condition/treatment.
- The previously considered interpretation of five unknown within-condition replicates is superseded.

## Consequence for n=220

The fact that the six XLSX files contain 220 numeric values no longer creates uncertainty about whether they are five iid replicates per group: they are not. However, `n=220` is still **not authorized as 220 independent fermentations**. The values belong to a structured design involving microorganism, carbon-source/cultivation level, temperature, response type and, for some assays, hydrophobic compound or biosurfactant:oil ratio.

The canonical dataset must therefore preserve that hierarchy and avoid flattening all numeric cells into one iid sample.

## Updated gate status

- B0-SOURCE/PROV at condition/treatment level: **PASS**.
- B0-SCHEMA at condition/treatment level: **PASS**.
- Semantics of `SAMPLE 1–5`: **RESOLVED — TREATMENT LEVELS**.
- Use of `SAMPLE 1–5` as biological/fermentation replicates: **PROHIBITED**.
- Use of all 220 numeric cells as iid fermentations: **BLOCKED**.
- Prospective EXT-D execution: **NOT YET AUTHORIZED**; first recanonicalize each workbook with explicit mapping from SAMPLE identifiers to treatment levels and preserve the preregistered post-M2 governance sequence.

## Scientific interpretation

The clarification strengthens Farias et al. as a prospective external-validation dataset because the source workbooks can now be interpreted as containing experimental treatment levels rather than ambiguous replicate rows. At the same time, the clarification makes the unit-of-analysis rule stricter: validation must operate on explicit experimental conditions/treatments, with any true replication treated as a separate hierarchical layer.

## Core status

No PEERFIX-Core file, generator, seed, threshold, metric, ICD rule, secondary model or adapter was changed.