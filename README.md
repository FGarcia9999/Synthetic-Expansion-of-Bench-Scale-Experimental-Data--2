# Synthetic Expansion of Bench-Scale Experimental Data — Safe Q1/Q2 Baseline v3

This repository stores the validated safe baseline for the biosurfactant synthetic data expansion workflow.

The active baseline is documented in `SAFE_BASELINE_MANIFEST.md`. Older/experimental files should remain outside the active workflow or be moved to `archive/`, `deprecated/`, or `old_runs/`.

Core interpretation of the validated baseline:

- Gaussian Copula showed the most stable utility–privacy balance.
- TVAE showed strong correlation/fidelity behavior, but higher proximity risk under 1% DOE-noise.
- CTGAN showed favorable privacy/tail-risk behavior, but weaker utility/fidelity.
- TabDDPM had the weakest utility and strongest degradation under noise.
- No validated ranking inversion was observed; the main effect is the magnitude of TSTR and the privacy trade-off.

Start with `docs/RUNBOOK_SAFE_BASELINE.md` to reproduce the validated figures and consolidated reports.
