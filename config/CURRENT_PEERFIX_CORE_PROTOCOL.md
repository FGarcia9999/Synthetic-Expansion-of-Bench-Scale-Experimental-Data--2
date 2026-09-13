# Current PEERFIX-Core protocol pointer

For all new Gate 0.3 and later work on branch `checkpoint/peerfix-core-v1-freeze-2026-09-13`, use:

`config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV1.yaml`

Do **not** use `config/PEERFIX_CORE_v1.0_PRE_FREEZE.yaml` for new execution. The original pre-freeze file is retained as an immutable historical checkpoint because its provenance block points to the dataset accidentally substituted during the CCE cleanup commit.

Derivation dataset currently authorized by provenance:

`data/derivation/peerfix2_historical_manuscript_dataset.csv`

SHA-256:

`c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`

Source confirmation: Souza (2009), UNICAP master's dissertation, Planning 2, factor levels in Table 4 and full 20-run matrix / surface-tension values in Table 8.

Quarantined dataset:

`data/quarantine/cleanup_substituted_dataset_6161c35.csv`

It is prohibited for Core derivation and external confirmation unless its independent provenance is established in a future audit.
