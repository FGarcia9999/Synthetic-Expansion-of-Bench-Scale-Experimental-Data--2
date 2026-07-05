# Minimal runbook for the safe Q1/Q2 baseline

## 1. Run the heavy expansion engine only if needed

The validated baseline assumes the two scenario folders already exist:

```text
exp_out_v5_doe0pct_tau010/
exp_out_v5_doe1pct_tau010/
```

Avoid changing the EXPAND script unless peer-review changes absolutely require it.

## 2. Generate Figures 1–3

```powershell
python .\code\generate_q1q2_figures_STANDALONE.py `
  --baseline ".\exp_out_v5_doe0pct_tau010" `
  --sensitivity ".\exp_out_v5_doe1pct_tau010"
```

## 3. Consolidate scenario report

```powershell
python .\code\q1q2_consolidate_reports.py `
  --baseline_bundle ".\exp_out_v5_doe0pct_tau010\bundle_q1q2" `
  --sensitivity_bundle ".\exp_out_v5_doe1pct_tau010\bundle_q1q2" `
  --outdir ".\_consolidated_q1q2" `
  --verbose
```

## 4. Generate Figures 4–5

```powershell
python .\code\generate_additional_q1q2_figures_FIXED.py `
  --baseline ".\exp_out_v5_doe0pct_tau010\evaluation_results.json" `
  --sensitivity ".\exp_out_v5_doe1pct_tau010\evaluation_results.json" `
  --outdir ".\_figures_additional"
```

## 5. Check final figure interpretation

- Fig. 4: privacy–utility trade-off.
- Fig. 5: utility/ranking summary.
- Confirm: `ΔRank = 0` for all generators.
