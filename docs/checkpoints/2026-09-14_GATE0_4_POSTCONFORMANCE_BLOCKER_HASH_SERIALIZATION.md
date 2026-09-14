# PEERFIX Gate 0.4 post-conformance audit blocker

Date: 2026-09-14
Branch: `resume/gate0.4-clean-derivation-2026-09-13`
Preflight run: `34868017734` — PASS
Scientific rerun: `34870216280` — workflow PASS
Scientific commit: `0c11bc0336458073659480d833fa5ec21a490ca0`
Protocol: `PEERFIX_CORE_v1.0_PRE_FREEZE_REV3`
Protocol SHA-256: `4ea74a46938f133db8e88ca2db446dc8d84f3815732709dbdb6c217dfa038e06`
Derivation dataset SHA-256: `c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

## What passed

- TabDDPM conformance preflight passed, including `tests/test_gate04_tabddpm_conformance.py`.
- Full scientific rerun completed successfully for both jobs (`utility` and `full-realisations`).
- All predeclared generator/scenario combinations were executed by the workflow.
- The scientific workflow executed from commit `0c11bc0336458073659480d833fa5ec21a490ca0` and uploaded both evidence artifacts.

## Blocking discrepancy

Gate 0.4 cannot receive final PASS and Gate 0.5 must not begin yet because the artifact-hash contract remains non-round-trip-verifiable.

`peerfix_core/hashing.py::hash_dataframe()` defines the dataframe digest over a canonical CSV serialization using:

```python
df.to_csv(index=False, lineterminator="\n", float_format="%.17g")
```

However, `scripts/gate04_derivation_runner.py` computes `synthetic_hash = hash_dataframe(synth)` and then persists each synthetic realisation with:

```python
synth.to_csv(synth_path, index=False)
```

The persisted file therefore is not guaranteed to be the exact canonical byte/text representation that was hashed. The same class of issue affects prediction hashes because hashes are computed over an in-memory canonical dataframe representation while the persisted prediction CSV is written independently with default pandas float serialization.

This is the same provenance/reproducibility blocker previously identified after the prior corrected run; the TabDDPM conformance patch did not modify the hashing/persistence layer. A successful Actions conclusion therefore does not resolve this blocker.

## Decision

**Gate 0.4: BLOCKED for final scientific PASS / final freeze.**

**Gate 0.5: NOT STARTED.**

No external confirmatory dataset is authorized before the freeze.

## Required corrective action

Apply a provenance-only patch, without changing models, seeds, protocol, hyperparameters, generators, CV geometry, thresholds, or scientific decision rules:

1. serialize each dataframe artifact with the exact canonical serialization used for hashing, or compute the manifest hash from the exact persisted bytes;
2. do the same for held-out predictions / prediction manifests;
3. add fail-closed round-trip tests verifying `persist -> reload/canonicalize -> hash` consistency;
4. repeat Gate 0.4 from the provenance-fixed commit;
5. audit artifact completeness, leakage, TRTR invariance, seed uniqueness, 10 unique Gaussian Copula baseline realisations, and hash reproducibility before authorizing Gate 0.5.

No outcome-driven tuning is permitted during this correction.
