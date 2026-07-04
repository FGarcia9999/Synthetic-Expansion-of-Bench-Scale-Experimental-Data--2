# Suggested GitHub cleanup commands

## 1. Create a preservation branch from the current repository state

```bash
git checkout -b baseline_q1q2_biosurfactant_final_working_v3
git add .
git commit -m "Mark safe Q1/Q2 biosurfactant baseline before peer-review changes"
git tag baseline_q1q2_biosurfactant_final_working_v3
git push origin baseline_q1q2_biosurfactant_final_working_v3 --tags
```

## 2. Create a working branch for peer-review changes

```bash
git checkout -b peer-review-orchestration-adjustments
```

## 3. Keep only the safe baseline files in active folders

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

## 4. Move older/non-final material aside

```bash
mkdir -p archive deprecated old_runs

# Examples only; adjust to real filenames:
git mv "*OLD*" archive/ 2>/dev/null || true
git mv "*old*" archive/ 2>/dev/null || true
git mv "*v2*" deprecated/ 2>/dev/null || true
git mv "*ranking_evolution_old*" deprecated/ 2>/dev/null || true
```

## 5. Do not keep as active files

- Old `generate_additional_q1q2_figures.py` that implied ranking inversion.
- Old `q1q2_consolidate_reports.py` before the v3 schema/figure fixes.
- Reports/abstracts stating:
  - "CTGAN superior" as the main result.
  - "TVAE 1st→3rd".
  - "Gaussian 2nd→1st".
  - "ranking reversal".
  - "TVAE collapses in utility" (the correct statement is privacy deterioration under noise).
