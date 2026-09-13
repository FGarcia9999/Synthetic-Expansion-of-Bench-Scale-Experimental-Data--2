# Current PEERFIX-Core protocol pointer

For all new Gate 0.4 and later work on branch `checkpoint/peerfix-core-v1-freeze-2026-09-13`, use:

`config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV2.yaml`

REV2 supersedes REV1 after Gate 0.3. The scientific change is explicit: stochastic downstream-model seeds are held constant across generators for the same scenario/repeat/fold/model, so generator identity cannot alter the real-only TRTR baseline.

Do **not** use `config/PEERFIX_CORE_v1.0_PRE_FREEZE.yaml` or REV1 for new execution. They are retained as immutable historical checkpoints.

Derivation dataset currently authorized by provenance:

`data/derivation/peerfix2_historical_manuscript_dataset.csv`

SHA-256:

`c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

Source confirmation: Souza (2009), UNICAP master's dissertation, Planning 2, factor levels in Table 4 and full 20-run matrix / surface-tension values in Table 8.

Quarantined dataset:

`data/quarantine/cleanup_substituted_dataset_6161c35.csv`

It is prohibited for Core derivation and external confirmation unless its independent provenance is established in a future audit.

Gate 0.3 qualification:
- CI run `34742387739`: PASS.
- Validated functional commit: `2539309303e8be3ab758d8b4d95d964a4a80d070`.
- Contract tests: 8 passed.
- Four-generator integration smoke: 5 passed, including actual Gaussian Copula, CTGAN, TVAE and TabDDPM fit/sample calls.
- Exact successful environment is preserved at `environment/gate03_environment_freeze.txt`.
