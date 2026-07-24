# Code

This clean branch is reserved for PEERFIX2/CCE-facing code only.

The full code package should include, at minimum:

- `q1q2_peerfix2_orchestrate.py`
- `q1q2_peerfix2_collect_fold_refit.py`
- `q1q2_peerfix2_cv_icd.py`
- `icd_domain_concordance.py`
- `generate_peerfix2_figures.py`
- the final synthetic-generation backend used by PEERFIX2

Historical PEERFIX1 scripts and audit-only scripts should not be included in this branch. They remain recoverable from `backup/pre-cce-v26-cleanup-peerfix1`.
