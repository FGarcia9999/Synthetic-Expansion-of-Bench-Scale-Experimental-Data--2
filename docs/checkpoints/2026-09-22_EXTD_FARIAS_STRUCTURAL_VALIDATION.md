# PEERFIX EXT-D — Farias structural validation after author clarification

Date: 2026-09-22
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
Status: **STRUCTURALLY VALIDATED AT CONDITION LEVEL — NO CORE EXECUTION AUTHORIZED**

## Sources reconciled

1. Farias et al. (2021), *PeerJ* 9:e12518, DOI `10.7717/peerj.12518`.
2. Six audited supplementary XLSX files (`s001`–`s006`) with SHA-256 values already frozen in the previous cell-level audit.
3. Direct author clarification from Charles Farias received on 2026-09-21/22 confirming that the culture conditions are those reported in Table 1 and that the microorganisms were evaluated under two growth temperatures, with microorganism-specific pH, agitation and fermentation time.
4. Previous audit report `PEERFIX_EXT1_Farias_Relatorio_Auditoria_v1.md`.

## Structural reconciliation

The 44 condition-response groups recovered in the prior audit can now be mapped coherently to the experimental structure of the paper:

### Surface tension — 32 condition cells

#### `s001` — *P. cepacia* CCT6659, block A (4 conditions)
- 2.0% canola frying oil + 3.0% corn steep liquor at 28 and 37 °C; pH 7.0; 250 rpm; 60 h.
- 5.0% glycerol + 2.0% glucose at 28 and 37 °C; pH 7.0; 200 rpm; 96 h.

#### `s002` — *P. cepacia* CCT6659, block B (6 conditions)
- 1.5%, 2.0% and 3.0% glucose, each at 28 and 37 °C; pH 7.0; 200 rpm; 96 h.

#### `s003` — *P. aeruginosa* UCP0992 (10 conditions)
- 1.5%, 2.0% and 3.0% glucose, plus 2.0% and 3.0% sucrose.
- Each medium was evaluated at 28 and 37 °C; pH 7.0; 200 rpm; 96 h.

#### `s004` — *P. aeruginosa* ATCC 10145 and ATCC 9027 (12 conditions)
- Two strains × three media × two temperatures.
- Media: 5.0% glycerol + 2.0% glucose; 1.0% n-hexadecane + 1.0% glucose; 2.0% sugar-cane molasses + 3.0% corn steep liquor.
- Temperatures: 28 and 35 °C; pH 7.0; 200 rpm; 96 h.

### Emulsification E24 — `s005` (6 condition cells)

- Two strains (ATCC 10145 and ATCC 9027) × three hydrophobic compounds (soybean, corn and motor oil).
- Biosurfactants were produced in 5.0% glycerol + 2.0% glucose for 96 h at 28 °C.

### Motor-oil dispersion — `s006` (6 condition cells)

- Two strains × three biosurfactant:oil ratios (1:2, 1:8 and 1:25).
- The previous audit showed that summary values in this workbook are hardcoded and partly inconsistent with recalculation. Therefore canonical values must be recalculated directly from the raw numeric cells.

## Updated gates

### B0-SOURCE/PROV — condition level: **PASS**

The dataset is publicly documented in PeerJ, the supplementary files are hash-frozen, and the author clarification is consistent with the published cultivation table. Provenance is sufficient for a condition-level external dataset.

### B0-SCHEMA — condition level: **PASS**

The 44 condition-response groups are now structurally mappable to organism, production medium, temperature, pH, agitation, fermentation time and response type.

### Raw five-value hierarchy: **HOLD**

The prior audit found five numeric values in every condition-response group. This remains unresolved at the statistical-unit level because:

- the article figures describe triplicate experiments;
- the statistical section states that triplicate results were expressed as mean ± SD;
- the E24 method section mentions four experiments;
- the XLSX files contain five numeric rows per group and no run/batch/flask identifiers.

The new author response confirms the culture-condition mapping but does **not** yet establish that the five numeric values are five independent fermentations. Therefore they must not be treated as iid experimental units.

### Use of `n=220` as iid observations: **BLOCKED**

The raw 220 numeric values remain unavailable for row-level predictive claims until their hierarchy is explicitly documented.

## Prospective EXT-D hierarchy before any PEERFIX execution

This hierarchy is based only on experimental structure, not on PEERFIX outcomes.

1. **Primary structural candidate: *P. aeruginosa* UCP0992 surface tension** — 10 condition cells with constant pH, agitation and fermentation time; factors vary mainly through medium composition and temperature.
2. **Secondary structural candidate: ATCC 10145/9027 surface tension** — 12 condition cells with strain, medium and temperature as explicit factors; process settings remain constant.
3. **Conditional candidate: *P. cepacia* surface tension** — 10 condition cells, but the canola/corn-steep condition differs simultaneously in fermentation time and agitation. These variables must remain part of the composite condition and cannot be interpreted as isolated effects.
4. **E24 and dispersion blocks** — retain as descriptive/domain-concordance candidates only until raw-value hierarchy is resolved; each contains only six condition cells.

## Governance decision

- No PEERFIX-Core file, generator, seed, threshold, ICD rule or model is changed.
- No EXT-D execution is authorized by this checkpoint.
- The M2 evidence chain remains unchanged; Farias remains outside the confirmatory M2 body.
- Before future EXT-D execution, create a dedicated preregistration/checkpoint that locks the selected block, response, factors, split strategy and treatment of the five raw values.
- All future results must be retained regardless of direction.

## Remaining author clarification needed

One final question remains scientifically important: what exactly are the five numeric rows present within each condition-response group in the XLSX files? Specifically, are they independent fermentations, technical measurements, sub-samples, or another nested structure, and how do they relate to the triplicate experiments described in the article?
