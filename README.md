# Synthetic Expansion of Bench-Scale Experimental Data — Safe Q1/Q2 Baseline v3

This repository stores the validated safe baseline for the biosurfactant synthetic data expansion workflow.

The active baseline is documented in `SAFE_BASELINE_MANIFEST.md`. Older/experimental files should remain outside the active workflow or be moved to `archive/`, `deprecated/`, or `old_runs/`.

**Current validated interpretation (PEERFIX1, branch `peer-review-revisions-v1`):** TVAE is the only
generator with a non-negative downstream-utility signal in both the baseline and 1% DOE-noise
sensitivity scenarios (point estimate sensitive to seed/hyperparameters — treated as a central
finding, not hidden; see `peer_review_investigation/DIAGNOSTICO_queda_utilidade_rerun_v4.md` and
manuscript Section 3.6). Gaussian Copula, CTGAN, and TabDDPM show no utility in any tested
configuration. The Domain-Grounded Concordance Index (ICD) does not rank TVAE first — no single
generator dominates utility, multivariate fidelity, domain concordance, and disclosure risk
simultaneously. Validated results: `runs/exp_out_v6_PEERFIX1_doe0pct/` and `..._doe1pct/`. An
earlier, superseded interpretation (produced by a pipeline with two now-corrected methodological
issues) is kept only in `archive/pre_peerfix1_outputs/README_HISTORICO.md`, for audit history —
not to be cited as current.

Start with `docs/RUNBOOK_SAFE_BASELINE.md` to reproduce the validated figures and consolidated reports.


