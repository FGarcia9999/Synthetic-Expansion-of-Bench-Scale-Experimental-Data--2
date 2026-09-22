# Farias clarification — treatment design confirmed; SAMPLE-row semantics still unresolved

Date: 2026-09-22
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## New author messages

Charles Farias provided additional clarification in direct correspondence and pointed again to Table 1 of Farias et al. (2021). He confirmed that the tested cultivation conditions were built from selected carbon-source conditions and organism-specific cultivation parameters, including pH, agitation, fermentation time and two temperatures. He also explained that the carbon-source values were chosen from literature and prior experimental experience, and that the measured productive characteristics were reported in the article figures (surface-tension reduction, emulsification, dispersion and CMC-related behavior).

## What is now resolved

1. The **treatment-design layer** is resolved. Table 1 is the authoritative mapping of microorganisms, production media/carbon sources, pH, agitation, fermentation time and temperature ranges.
2. The previous condition-level reconstruction remains valid: 32 surface-tension condition groups, 6 E24 groups and 6 motor-oil-dispersion groups across the six supplementary XLSX files.
3. The public article states that raw measurements are available in the supplementary files, so the supplementary XLSX files remain the appropriate numeric source rather than digitized figure values.
4. The condition-level schema can therefore remain `PASS` for provenance and structural mapping.

## What is **not** yet resolved

The latest answer does **not explicitly resolve the statistical meaning of the five numeric rows labelled `SAMPLE 1` ... `SAMPLE 5` inside each supplementary condition group**.

This distinction is critical. Charles's explanation addresses why the carbon-source levels/cultivation conditions were chosen. It does not state whether, for one fixed condition (for example, one medium at one temperature), the five spreadsheet values are:

- five independent fermentations;
- five analytical/technical readings from one fermentation;
- means or summaries of triplicate fermentations;
- five subsamples/tubes from a larger experimental unit;
- or another nested structure.

The published article/figure legends refer to triplicate experiments, and one E24 methods statement mentions four experiments, whereas the supplementary XLSX audit found five numeric values in every condition group. Therefore the five rows cannot yet be treated as independent experimental units.

## Current gate decisions

- `B0-SOURCE/PROV (condition level)`: **PASS**
- `B0-SCHEMA (condition level)`: **PASS**
- `SAMPLE 1–5 independence`: **HOLD**
- `n=220 as iid observations`: **BLOCKED**
- condition-level use: **AUTHORIZED FOR STRUCTURAL/DESCRIPTIVE WORK ONLY**
- PEERFIX-Core execution on Farias: **NOT YET AUTHORIZED**

## Recommended final author question

To avoid further semantic ambiguity, ask a single condition-specific question with one screenshot/cell example from a supplementary workbook, for example:

> In Supplementary Information 2, take one fixed condition such as *P. aeruginosa* UCP0992 grown in 1.5% glucose at 28 °C. The XLSX contains five numerical values under SAMPLE 1–5 for that fixed condition. What do those five values represent exactly? (A) five independent fermentation broths; (B) five analytical readings from the same broth; (C) means of triplicate fermentations; or (D) another structure? If (C) or (D), please describe what was averaged or repeated.

Only after this point is answered can row-level analysis be considered without risk of pseudoreplication.

## Governance

No PEERFIX-Core file, generator, seed, threshold, ICD rule, metric, downstream model or adapter was modified. The Farias data remain outside the required evidence chain of Manuscript 2 and remain a prospective/conditional EXT-D candidate.