# External validation analysis tables

This directory contains **run-level canonical analysis tables** used by the post-freeze PEERFIX external-validation workflows. They deliberately exclude author-supplied raw workbooks and any within-run measurements that were not already part of the published run-level result structure.

## Governance

- The author-supplied XLSX workbooks remain outside the public repository unless separate public-redistribution permission is documented.
- The workbook SHA-256 identities are recorded in `config/external/*_ADAPTER_*.yaml` and the author-contact audit records.
- These CSVs are minimal computational analysis tables: DOE run/factor coding plus the run-level response(s) needed by the preregistered validation.
- Source observations remain attributable to the original publications/authors. **This directory does not relicense source observations under the repository-wide CC BY statement.** The repository license applies only to PEERFIX-created code, documentation, derived summaries, and validation outputs unless the source license independently permits redistribution.
- Synthetic rows produced by the workflows are computational outputs, not new biological experiments.

## Files

- `ext_a_c_mogii_run_level.csv`: 27-run four-factor CCD; target `STred_mNm`. No ST1/ST2/ST3 raw within-run readings are included.
- `ext_b_c_utilis_run_level.csv`: 19-run full 2^4 + three centers; run-level mean responses Y1/Y2/Y3. No unavailable within-run replicates are inferred.

The tables are frozen before generator execution and are checked by SHA-256 in the external runner.