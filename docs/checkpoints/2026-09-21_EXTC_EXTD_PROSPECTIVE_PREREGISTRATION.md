# PEERFIX — Prospective EXT-C / EXT-D preregistration

Date: 2026-09-21
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## Scope

This checkpoint preregisters two prospective post-M2 external-validation routes. It does **not** authorize PEERFIX execution, does not modify Manuscript 2, and does not alter or retune PEERFIX-Core v1.0.

The purpose is to prevent post-outcome dataset selection. EXT-C and EXT-D have distinct identities. All outcomes, including negative outcomes, modelability blocks and provenance blocks, must be retained.

## EXT-C — fixed prospective candidate

Source: Fontes GC, Amaral PFF, Nele M, Coelho MAZ. *Factorial Design to Optimize Biosurfactant Production by Yarrowia lipolytica*. BioMed Research International. 2010;2010:821306. DOI: `10.1155/2010/821306`.

Preregistered primary dataset:
- Carbon-source 2^4 full factorial design reported in Table 4 of the source article.
- 19 experimental units: 16 factorial combinations + 3 center-point experiments.
- Factors: glycerol, olive oil, hexadecane and glucose.
- Primary response: emulsification index (EI, %).
- Secondary response: maximum variation in surface tension (ΔST, mN m−1).
- The later 2^2 central composite optimization is excluded from primary EXT-C and will not be substituted if the 2^4 outcome is unfavorable.

Selection rationale was fixed before PEERFIX execution: the design matrix is public, complete, small-sample, biosurfactant-focused, and independent of a private workbook. It is close in size to the C. utilis external dataset while using a biologically distinct system.

## EXT-D — conditional prospective candidate

Source: Farias CBB et al. *Removal of heavy oil from contaminated surfaces with a detergent formulation containing biosurfactants produced by Pseudomonas spp.* PeerJ. 2021;9:e12518. DOI: `10.7717/peerj.12518`.

Current audit state:
- 6 supplementary XLSX files.
- 44 condition-response groups.
- 220 numeric values, with 5 values in every group.
- Previous audit did not allow treatment of the 220 values as iid observations because SAMPLE 1–5 lacked explicit experimental-unit semantics.

New author clarification:
- Five cultivation conditions were used for each experiment.
- Conditions had specific agitation/rotation, fermentation time and growth temperature.
- Conditions were performed in triplicate.

Remaining provenance gate before any EXT-D execution:
1. Confirm SAMPLE 1 … SAMPLE 5 map exactly to the five cultivation conditions.
2. Confirm whether each SAMPLE value is the aggregate/result of three independent fermentation experiments or a repeated analytical reading from one fermentation.
3. Map agitation/rotation, fermentation time and temperature to SAMPLE 1 … SAMPLE 5.
4. Confirm whether triplicates were independent fermentation/biological replicates and whether they were aggregated before entry into the XLSX files.

Until this gate is resolved, `n=220 iid` remains forbidden. The only safe interim interpretation is condition-level.

If provenance fails, EXT-D is recorded as `BLOCKED_BY_PROVENANCE / EXPERIMENTAL_UNIT`. No replacement dataset may be selected post hoc because of a desired PEERFIX outcome.

## Frozen analysis rules for EXT-C / EXT-D

- No change to generator families, random seeds, thresholds, ICD rules, downstream models, validation logic or decision rules in PEERFIX-Core v1.0.
- No generator-specific optimization after viewing prospective outcomes.
- Adapters may perform only semantic mapping, unit harmonization, experimental-unit definition and source-preserving canonicalization.
- Test/validation information may not return to synthetic generation or model fitting.
- Results must distinguish absolute predictive validity, relative change, domain-grounded concordance, distributional checks and coverage/proximity diagnostics.
- A positive result on one axis is not global validation.
- All outputs, hashes and audit logs must be committed before interpretive rewriting.

## Response order if EXT-D becomes eligible

1. Primary block: surface tension.
2. Secondary block: emulsification index (E24).
3. Tertiary block: motor-oil dispersion.
4. Different microorganisms/substrates remain explicit experimental blocks and are not pooled merely to increase sample size.

## Separation from Manuscript 2

Neither EXT-C nor EXT-D is required for the scientific validity or submission of Manuscript 2. Both are prospective post-M2 work and must not delay the M2 scientific freeze or journal submission.

## Graphical abstract terminology closure

The M2 graphical abstracts were updated without changing their scientific content. The bottom take-home statement now avoids the informal `adding rows / adicionar linhas` phrasing.

EN final wording:
`Synthetic data augmentation is not the same as performing new fermentations.`

PT final wording:
`Aumentar os dados sinteticamente não é o mesmo que realizar novas fermentações.`

## Artifact hashes

- `PEERFIX_EXTC_EXTD_Prospective_Preregistration_EN_v1.docx`
  SHA-256: `951e17764855db9affcf7ac711d54182ec37804db01e0d9c5cab211885aa8e2b`
- `PEERFIX_EXTC_EXTD_PreRegistro_Prospectivo_PT_v1.docx`
  SHA-256: `78a42bb11aad68b48c0804a1b90772624eacdae2f7690b6b69e352a8ce3f2af3`
- `Graphical_Abstract_EN_FINAL_TERMINOLOGY.png`
  SHA-256: `feaed42f275b25212267a09f1a90c3d05fa353a216e7fd276db606a4e0a47822`
- `Graphical_Abstract_PT_FINAL_TERMINOLOGY.png`
  SHA-256: `15e3abe9ac956624fddbcd50a6be948f3506981fc64af22161a60b1a3d1d835e`
- Combined package:
  SHA-256: `5c00b8cd1c79c6204267288bd1b6093fb45380942c94614fe8ff4daf43e4c576`

## Decision

Status: `PREREGISTERED — NO EXECUTION AUTHORIZED`.

Next allowed actions:
1. Finish M2 scientific freeze and submission package.
2. Obtain final author clarification for Farias SAMPLE 1–5.
3. Only after M2 freeze, lock the EXT-C source table/checksum and begin prospective execution under the frozen v1.0 Core.
4. EXT-D may proceed only if its provenance/experimental-unit gate passes, regardless of the EXT-C outcome.