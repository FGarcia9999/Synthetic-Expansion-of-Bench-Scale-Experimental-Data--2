# PEERFIX-EXT — Peterson / Candida mogii author-confirmed dataset audit

Date: 2026-09-14
Branch: `resume/gate0.4-clean-derivation-2026-09-13`
Status: SOURCE/PROVENANCE QUALIFIED FOR POST-FREEZE EXTERNAL VALIDATION

## 1. Author authorization and provenance

Peterson Felipe Ferreira da Silva reported that he consulted the corresponding author, Prof. Jenyffer Guerra, and that she agreed with the transfer/use of the data. He supplied the recovered original experimental workbook and explained that it contains the complete 27-run design matrix in coded and real units, three surface-tension replicates per run, calibration STw, recalculated STexp, STred, and point type.

The supplied workbook is `DOE_Artigo Foods (def) Peterson.xlsx`.

Local SHA-256 of the supplied workbook:
`1ed8bb86457c613cb8fa14b2b836e95ff40c82529749f8e258b987adfdd0a33f`

Important governance note: permission to use/transfer the data is documented. Public redistribution of the raw workbook is not assumed automatically from that permission; therefore the workbook itself is not committed to this public repository at this stage.

## 2. Recovered design geometry

The workbook contains exactly 27 experimental runs:
- 16 factorial points;
- 8 axial points;
- 3 center points.

Four coded factors are present:
- A = Licuri oil;
- B = Glucose;
- C = Ammonium nitrate;
- D = Yeast extract.

Each coded factor takes values `-2, -1, 0, +1, +2`, confirming a four-factor central composite / response-surface design with axial distance alpha = 2.

Recovered coded-to-real mappings:
- A: `-2=0.5`, `-1=2`, `0=3.5`, `+1=5`, `+2=6.5` %;
- B: `-2=1`, `-1=4`, `0=7`, `+1=10`, `+2=13` %;
- C: `-2=0.05`, `-1=0.2`, `0=0.35`, `+1=0.5`, `+2=0.65` %;
- D: `-2=0.05`, `-1=0.2`, `0=0.35`, `+1=0.5`, `+2=0.65` %.

This independently confirms the author's clarification that the published Table 1 label of axial levels as ±1.41 is a typographical error; the actual concentrations correspond to ±2 in coded units.

## 3. Response reconstruction and arithmetic integrity

For every one of the 27 runs, the workbook provides `ST1`, `ST2`, and `ST3`, plus their mean (`ST (med)`).

Audit results:
- the arithmetic mean of ST1–ST3 matches `ST (med)` exactly for all 27 runs (maximum absolute discrepancy = 0);
- `STw` is implicitly constant at exactly `71.179 mN/m` for all runs;
- `STred = 71.179 - ST(med)` is satisfied exactly for all 27 runs;
- residual = observed STred − predicted STred is satisfied exactly for all 27 runs.

Run-level response precision is high:
- mean within-run SD across the three ST readings ≈ `0.165 mN/m`;
- median within-run SD ≈ `0.148 mN/m`;
- maximum within-run SD = `0.399 mN/m`;
- mean within-run CV ≈ `0.421%`;
- maximum within-run CV ≈ `1.127%`.

The 27 DOE runs, not the 81 individual ST readings, are the correct experimental-unit level for modeling unless additional experimental-unit metadata proves otherwise. The three ST readings are preserved as within-run replicate measurements and must not be promoted to 81 independent DOE observations.

## 4. Independent reconstruction of the published quadratic model

A full quadratic OLS model was reconstructed from the 27 run-level STred values using coded factors:
intercept + A+B+C+D + all 6 two-way interactions + A²+B²+C²+D².

Reconstructed coefficients (before publication rounding):
- Intercept = `31.29133333`
- A = `+0.13395833`
- B = `-0.51929167`
- C = `+0.15370833`
- D = `+3.40862500`
- AB = `-1.14943750`
- AC = `+0.59506250`
- AD = `+1.81043750`
- BC = `-1.43318750`
- BD = `-1.98106250`
- CD = `+0.76593750`
- A² = `-0.31592708`
- B² = `+0.06469792`
- C² = `+0.10219792`
- D² = `-0.59655208`

These reproduce the workbook/Design-Expert coefficient table to its displayed rounding.

Reconstructed model diagnostics:
- SSE = `28.00268342` (workbook: 28.00);
- total SS = `510.69956452` (workbook: 510.70);
- model SS = `482.69688110` (workbook: 482.70);
- R² = `0.94516799` (workbook: 0.9452);
- adjusted R² = `0.88119731` (workbook: 0.8812);
- PRESS = `155.53384530`;
- predicted R² = `0.69544943` (workbook: 0.6954);
- residual SD = `1.52759843` (workbook: 1.53);
- CV = `4.98749%` (workbook: 4.99%).

Center-point pure error is independently recovered from the three center runs:
- center STred values = `30.321`, `31.438`, `32.115`;
- center mean = `31.29133333`;
- pure-error SS = `1.64148467`, df = 2;
- lack-of-fit SS = `26.36119875`, df = 10;
- lack-of-fit F ≈ `3.21187`, consistent with the workbook reported p = 0.2607.

The workbook's predicted values agree with the independently reconstructed quadratic model within at most `0.0005 mN/m`, attributable to displayed rounding.

## 5. Domain-effect fingerprint available for external validation

At p < 0.05 in the supplied ANOVA, the source-confirmed quadratic model identifies:
- D (Yeast extract): positive main effect, p < 0.0001;
- AB: negative interaction, p = 0.0109;
- AD: positive interaction, p = 0.0005;
- BC: negative interaction, p = 0.0028;
- BD: negative interaction, p = 0.0002.

CD is borderline (`p = 0.0680`) and should not be promoted into the primary confirmed-effect set without preregistration. A, B, C, AC, and all quadratic terms are nonsignificant at 0.05 in the reported full quadratic model.

This source-confirmed coefficient/sign/significance pattern can serve as an external-domain concordance fingerprint after PEERFIX-Core freeze. It must be preregistered before any external synthetic expansion is executed.

## 6. Gate implications

### B0-SOURCE/PROV
**PASS** for analysis/use: author/corresponding-author agreement is documented, and the original laboratory/design workbook was recovered.

### B0-SCHEMA
**PASS at run level**: the 27-run experimental design is explicit, coded and real factor values are available, point type is available, and three ST readings are linked to each run.

### Response definition
- canonical primary response for external PEERFIX analysis: `STred` at the 27-run level;
- `STexp` is not needed for modeling because, with constant STw = 71.179 mN/m, it is an exact linear transform of STred;
- ST1–ST3 are retained as within-run measurement information, not promoted to independent DOE rows.

### Geometry
The dataset is especially valuable because its CCD/response-surface geometry is different from the PEERFIX2 derivation full 2^4 factorial + centers. It therefore provides a genuine transportability challenge rather than a near-copy of the development geometry.

### Current ranking
Pending the Charles Farias clarification and the unresolved Livia/Candida utilis provenance question, this author-confirmed Candida mogii dataset becomes the strongest currently qualified candidate for the **primary post-freeze external validation**.

## 7. Freeze firewall

No PEERFIX generator, threshold, ICD rule, hyperparameter, CV geometry, or decision rule may be modified using this external dataset. The dataset may be used only after Gate 0.5 final Core freeze, under a preregistered external-validation adapter/protocol.

Recommended post-freeze first actions:
1. create a canonical 27-run adapter preserving run order, point type, coded/real factors, ST1–ST3, STmean, STw, and STred;
2. freeze the external-domain reference-effect set and decision rules before generator execution;
3. run external validation without retuning PEERFIX-Core;
4. retain the raw workbook hash/provenance and a non-redistribution flag until explicit public-redistribution permission is documented.
