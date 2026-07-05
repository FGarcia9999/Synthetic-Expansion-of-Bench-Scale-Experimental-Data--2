# Suggested GitHub cleanup commands

## 1. Use this repository as the clean baseline

This repository was initialized to keep only the validated safe Q1/Q2 biosurfactant baseline.

Recommended active structure:

```text
code/
data/
outputs/figures/
outputs/reports/
docs/
SAFE_BASELINE_MANIFEST.md
README.md
```

## 2. If importing material from older repositories, move non-final files aside

```bash
mkdir -p archive deprecated old_runs
```

Move older/non-final material to:

- `archive/` for historical runs and old outputs.
- `deprecated/` for replaced scripts.
- `old_runs/` for previous scenario folders.

## 3. Do not keep as active files

- Old `generate_additional_q1q2_figures.py` that implied ranking inversion.
- Old `q1q2_consolidate_reports.py` before the v3 schema/figure fixes.
- Reports/abstracts stating:
  - "CTGAN superior" as the main result.
  - "TVAE 1st→3rd".
  - "Gaussian 2nd→1st".
  - "ranking reversal".
  - "TVAE collapses in utility".

Correct interpretation: TVAE improves utility under noise but deteriorates in privacy/proximity; Gaussian Copula is the most stable utility–privacy option in the validated baseline.

## 4. Recommended branch strategy

```bash
git checkout -b peer-review-orchestration-adjustments
```

Use that branch for new peer-review changes. Keep this main baseline stable until the new orchestration is validated.
