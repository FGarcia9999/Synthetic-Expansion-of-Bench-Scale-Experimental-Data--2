# Synthetic Expansion of Bench-Scale Experimental Data on Biosurfactant Production

This branch is the clean **PEERFIX2 / CCE submission-facing branch** for the manuscript:

**Synthetic Expansion of Bench-Scale Experimental Data on Biosurfactant Production Using Tabular Generative Models: Trade-offs Between Fidelity, Utility, and Domain-Grounded Validation**

## Scope

The study evaluates whether tabular synthetic-data expansion can complement a very small bench-scale Design-of-Experiments dataset (`n = 20`) on bioemulsifier/biosurfactant production by *Candida lipolytica* UCP 988, using surface tension as the primary response.

The final validation workflow is **PEERFIX2**, a no-leakage protocol combining:

- repeated k-fold fold-refit utility validation;
- TSTR, TRTR, and same-model Delta;
- proximity-risk diagnostics based on Distance to Closest Record (DCR);
- a Domain-Grounded Concordance Index (ICD) for factorial-effect preservation.

## Scientific message

No generator dominates all validation objectives. Gaussian Copula provides the most stable repeated-k-fold utility, TVAE best preserves domain-grounded concordance, and CTGAN illustrates why positive gain over a weak real-only baseline is not equivalent to robustly positive absolute prediction.

The central conclusion is that statistical fidelity, downstream utility, gain over a real-only baseline, proximity risk, and domain-grounded scientific validity must be evaluated separately.

Synthetic expansion is treated here as an auditable complement to bench-scale experimental design, not as a replacement for physical experimental replication.

## Branch status

Historical PEERFIX1 and pre-PEERFIX2 materials were intentionally removed from this clean branch to avoid reviewer confusion. A complete backup of the previous repository state was preserved in the branch:

`backup/pre-cce-v26-cleanup-peerfix1`

This branch should contain only PEERFIX2/CCE-facing metadata, final data descriptors, final result tables, reproducibility notes, and release/Zenodo metadata.

## Citation

Citation metadata are provided in `CITATION.cff`. A citable Zenodo DOI will be added after the corresponding GitHub release is archived through Zenodo.

## Licensing

This repository uses dual licensing:

- **Source code:** MIT License. See `LICENSE`.
- **Data, figures, tables, manuscripts, supplementary material, and non-code documentation:** Creative Commons Attribution 4.0 International License (CC BY 4.0). See `LICENSE-DATA-DOCS.md`.

Zenodo metadata are provided in `.zenodo.json`.

## Authors

- Fernando Antonio Marçal Garcia — ORCID: 0000-0003-0461-0431
- Fabiana América Silva Dantas de Souza — ORCID: 0009-0008-2186-8649
- Galba Maria Campos-Takaki — ORCID: 0000-0002-0519-0849
- Clarissa Daisy da Costa Albuquerque — ORCID: 0000-0002-5492-2559

## Reproducibility note

The final utility results are based on repeated k-fold fold-refit validation. In each fold, synthetic data are generated only from the real training subset and evaluated on held-out real observations. This avoids train-test leakage and supports auditable comparison of utility, domain concordance, and proximity risk.

## Release note

For a single GitHub/Zenodo release, create a GitHub release from this clean branch after the final manuscript, figures, supplementary tables, and code package are uploaded. Zenodo should archive that release as one record.
