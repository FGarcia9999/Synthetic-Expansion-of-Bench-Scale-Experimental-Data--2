# PEERFIX — Farias author clarification (partial resolution)

Date: 2026-09-21
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## New author clarification

Charles Farias clarified in direct correspondence that the study involved multiple carbon-source conditions across four microorganisms. He further stated that five cultivation conditions were used for each experiment, with specific rotation/agitation, fermentation time and growth temperature, and that all conditions were performed in triplicate.

This materially improves the experimental interpretation of the supplementary spreadsheets, but it does **not yet fully resolve** the meaning of the spreadsheet rows labelled `SAMPLES 1–5`.

## Why the issue is only partially resolved

The previous cell-level audit found six supplementary XLSX files, 44 condition–response groups and five numeric rows in every group (220 raw numeric values). The source workbooks do not contain hierarchical identifiers such as run/batch/flask IDs. The published article describes triplicate experiments, while one method section also mentions four experiments. Therefore the five spreadsheet rows could not previously be identified as independent experimental units, technical readings, condition means, or another nested structure.

Charles's new statement strongly suggests that there were five cultivation conditions and that triplicate experiments were associated with them. However, one final mapping is still required before the five spreadsheet rows can be reclassified safely.

## Required final clarification

Ask the source author to confirm explicitly:

1. Do `SAMPLE 1` ... `SAMPLE 5` in the supplementary XLSX correspond exactly to the five distinct cultivation conditions described in the correspondence?
2. Is each `SAMPLE n` value the mean/result of three **independent fermentation experiments** performed under that condition, or is it one of several repeated analytical readings from a single fermentation?
3. What are the rotation/agitation, fermentation-time and growth-temperature settings associated with SAMPLE 1 ... SAMPLE 5?
4. Are the triplicates independent biological/fermentation replicates, and were they aggregated before entry into the XLSX?

## Current decision

- **Do not treat the 220 spreadsheet values as iid observations yet.**
- The previous safe condition-level interpretation remains valid until the mapping above is confirmed.
- Farias remains outside the required evidence chain of Manuscript 2. This avoids changing the nearly frozen M2 scope because of a late clarification.
- If the final mapping confirms five distinct cultivation conditions with independent triplicate fermentations, Farias becomes a substantially stronger candidate for a **prospective post-M2 external validation**.
- Any prospective use must be preregistered before PEERFIX execution, with the Core v1.0 remaining frozen and all results retained regardless of direction.

## Relationship to the planned EXT-C literature route

The planned literature-based prospective candidate (e.g. Fontes et al. 2010 / related biosurfactant DoE datasets) remains useful because it provides a clean public design matrix and a pre-outcome selection rationale. Farias, if fully clarified, offers a complementary and potentially more heterogeneous validation setting. The two should not be selected post hoc based on which produces a favorable PEERFIX result.

## Core status

No PEERFIX-Core file, generator, seed, metric, threshold, ICD rule, model or adapter was changed by this clarification.