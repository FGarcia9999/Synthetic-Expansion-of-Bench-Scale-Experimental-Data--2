# Current PEERFIX-Core protocol pointer

For all new Gate 0.4 work on branch `resume/gate0.4-clean-derivation-2026-09-13`, the executable pre-freeze protocol is the ordered pair:

1. `config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV2.yaml`
2. `config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV3_AMENDMENT.yaml`

The manifest label is `PEERFIX_CORE_v1.0_PRE_FREEZE_REV3`. Its protocol identity is the SHA-256 of the two raw files concatenated in the declared order with a single newline separator. Gate 0.5 will consolidate the accepted specification into one final frozen YAML.

REV2 remains the complete base protocol and carries the Gate 0.3 correction that stochastic downstream-model seeds are invariant to generator identity for the same scenario/repeat/fold/model. REV3 adds only the exact executable semantics of the historical PEERFIX2 `sensitivity_1pct` derivation sensitivity.

REV3 sensitivity semantics:
- perturb only the declared response `surface_tension_mNm`;
- keep all four DOE factors unchanged;
- use Gaussian zero-mean jitter with sigma = 1% of the response range in the explicit real calibration data;
- during utility validation, calibrate from the real training fold only;
- during full-realisation derivation analysis, calibrate from the full authorized real derivation dataset;
- use a deterministic perturbation RNG stream derived from the generator seed;
- do **not** clip the response to the observed real-data range.

This differs intentionally from the legacy implementation, which inferred discrete columns by cardinality and clipped perturbed values to the real min/max. The no-clipping change is required by the predeclared REV2 target postprocessing rule and prevents artificial truncation of synthetic response tails.

Do **not** use `config/PEERFIX_CORE_v1.0_PRE_FREEZE.yaml`, REV1, or REV2 alone for new Gate 0.4 execution. They remain immutable historical checkpoints.

Derivation dataset authorized by provenance:

`data/derivation/peerfix2_historical_manuscript_dataset.csv`

SHA-256:

`c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

Source confirmation: Souza (2009), UNICAP master's dissertation, Planning 2, factor levels in Table 4 and full 20-run matrix / surface-tension values in Table 8.

Quarantined dataset:

`data/quarantine/cleanup_substituted_dataset_6161c35.csv`

It remains prohibited for Core derivation and external confirmation unless its independent provenance is established in a future audit.

Gate 0.3 qualification remains PASS:
- protocol-aligned CI run `34742575894`: success;
- four executable generator families qualified: Gaussian Copula, CTGAN, TVAE and PEERFIX small-n TabDDPM;
- qualified environment snapshot: `environment/gate03_environment_freeze.txt`.

Gate 0.4 may proceed only after the new sensitivity contract tests and fail-closed derivation-runner preflight pass. External confirmatory execution remains prohibited until Gate 0.5 final freeze.
