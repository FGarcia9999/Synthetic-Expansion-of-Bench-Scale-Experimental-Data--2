# PEERFIX EXT-C — Fontes pre-execution gate

Date: 2026-09-22
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`

## Scope

This checkpoint closes the source canonicalization, modelability and adapter-representability gates for the preregistered EXT-C candidate. It does not alter PEERFIX-Core v1.0 and does not reinterpret Manuscript 2.

Source: Fontes GC, Amaral PFF, Nele M, Coelho MAZ. *Factorial Design to Optimize Biosurfactant Production by Yarrowia lipolytica*. BioMed Research International. 2010;2010:821306. DOI `10.1155/2010/821306`.

The preregistered source is Table 4 only: carbon-source 2^4 full factorial design, 16 factorial combinations plus 3 center-point experimental assays. The later 2^2 central-composite optimization remains excluded from primary EXT-C.

## Canonical data lock

File: `data/external/ext_c_fontes_carbon_2pow4.csv`
SHA-256: `41dba19fe743147ab249951c2e388a2f6c0647fa55af7b306e7fe54223f2f5d2`

Factors, coded exactly as in the source design:
- `z1_glycerol`: -1/0/+1 = 0/1/2 %
- `z2_olive_oil`: -1/0/+1 = 0/2/4 %
- `z3_hexadecane`: -1/0/+1 = 0/1/2 %
- `z4_glucose`: -1/0/+1 = 0/2/4 %

Responses:
- primary: `EI_pct`
- secondary: `delta_ST_mNm`

Experimental unit: one experimental assay. The three center-point assays remain separate experimental units for experiment-wise validation and a single grouped condition for grouped-condition validation.

## Modelability gate

The preregistered reconstruction uses the fixed model `main effects + all two-way interactions`, without outcome-driven term search.

### EI — primary response
- n = 19
- model rank = 11
- residual df = 8
- R2 = 0.9931355444
- adjusted R2 = 0.9845549748
- global p = 1.5204063e-07
- leave-one-assay-out R2 = 0.9376775869
- LOO RMSE = 5.1670037116
- decision: `PASS_MODELABILITY`

### Delta surface tension — secondary response
- n = 19
- model rank = 11
- residual df = 8
- R2 = 0.9619701052
- adjusted R2 = 0.9144327367
- global p = 0.00012942956
- leave-one-assay-out R2 = 0.7285102096
- LOO RMSE = 3.1919253800
- decision: `PASS_MODELABILITY`

## Adapter representability gate

Adapter: `config/external/03_ADAPTER_FONTES_EXT_C.yaml`
Local artifact SHA-256 before repository insertion: `76687f59c01752dd9bfe5a9e8278cb5dd14eda81e33b0a45dfb3b3196a5ef920`

Decision: `PASS`.

Rationale:
- all four factors are quantitative and source-coded as -1/0/+1;
- no nominal/categorical encoding is needed;
- no artificial ordinal geometry is introduced;
- the frozen numeric support/snap contract can represent all four factors directly;
- there are 17 unique factor tuples, sufficient for grouped five-fold validation;
- the three center assays can be kept together under grouped-condition CV.

This contrasts with EXT-D/Farias, where the categorical medium factor cannot be represented neutrally by the v1.0 numeric-factor contract. Farias therefore remains a scientifically useful `BLOCKED_BY_ADAPTER_REPRESENTABILITY` boundary case rather than being forced through an invalid encoding.

## Execution harness

The original `scripts/external_validation_runner.py` and `scripts/external_audit.py` were not modified.

EXT-C is registered through thin wrappers only:
- `scripts/ext_c_validation_runner.py`
- `scripts/ext_c_external_audit.py`

These wrappers add dataset identifiers and expected hashes/n only. They call the existing external runner/auditor unchanged.

Workflow:
- `.github/workflows/external-c-fontes.yml`
- same four generators: Gaussian Copula, CTGAN, TVAE, TabDDPM;
- same master seed, repetitions, synthetic n, model panel, ICD matched-n logic, DCR/fidelity bundle and CV logic;
- both experiment-wise and grouped-condition validation;
- no retuning or generator-specific optimization.

## Decision

EXT-C passes source, modelability and adapter-compatibility gates for both preregistered responses.

Status: `PREEXECUTION_PASS — EXECUTION MAY BE AUTHORIZED`.

All favorable and unfavorable generator outcomes must be retained. The carbon-source 2^2 CCD published later in the same article may not replace this 2^4 EXT-C if the prospective result is unfavorable.
