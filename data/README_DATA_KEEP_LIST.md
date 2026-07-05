# Data files to keep in the public reproducibility branch

Use this folder for the minimal datasets needed to reproduce the validated Q1/Q2 baseline.

## Keep

1. Original experimental DOE dataset
   - `experimental database.xlsx` or a normalized CSV equivalent.
   - Recommended canonical name: `data/experimental_database.xlsx`

2. Synthetic data generated from the validated final run
   - Baseline scenario (0% DOE noise):
     - `data/baseline/gaussian_copula_synthetic.csv`
     - `data/baseline/ctgan_synthetic.csv`
     - `data/baseline/tvae_synthetic.csv`
     - `data/baseline/tabddpm_synthetic.csv`
   - Sensitivity scenario (1% DOE noise):
     - `data/sensitivity/gaussian_copula_synthetic.csv`
     - `data/sensitivity/ctgan_synthetic.csv`
     - `data/sensitivity/tvae_synthetic.csv`
     - `data/sensitivity/tabddpm_synthetic.csv`

3. Validated scenario outputs, if the repository is intended to reproduce the manuscript figures directly:
   - `outputs/baseline/evaluation_results.json`
   - `outputs/baseline/experiment_config.json`
   - `outputs/sensitivity/evaluation_results.json`
   - `outputs/sensitivity/experiment_config.json`

## Avoid / move aside

- Old synthetic CSVs without scenario label (`baseline` vs `sensitivity`).
- Old figures/texts that claim ranking inversion (TVAE 1st→3rd; Gaussian 2nd→1st).
- Deprecated scripts replaced by the safe baseline listed in `SAFE_BASELINE_MANIFEST.md`.

Note: raw Excel/CSV data files should be copied from your local environment into the canonical paths above.
