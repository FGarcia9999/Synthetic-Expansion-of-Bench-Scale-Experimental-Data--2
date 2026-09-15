# Gate 0.5 — PASS and final PEERFIX-Core v1.0 freeze

Date: 2026-09-15

## Decision

**PASS. PEERFIX-Core v1.0 is formally frozen.**

Gate 0.5 workflow run `34984504198` completed successfully from freeze-candidate commit `82fd49bd3b91edf5ff9049b11f21dec02caa6e11` on branch `freeze/peerfix-core-v1.0-2026-09-15`.

## Gate 0.5 evidence

- Protected scientific implementation unchanged relative to final Gate 0.4 scientific validation commit `74b827768e0401de2aa24fb30bc69896dca6ae6b`: PASS.
- Qualified derivation dataset identity: PASS; SHA-256 `c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`.
- Executable protocol identity: PASS; SHA-256 `4ea74a46938f133db8e88ca2db446dc8d84f3815732709dbdb6c217dfa038e06`.
- Frozen manifest anchors: PASS.
- Full Core/Gate 0.4 contract test suite: PASS (`35 passed`).
- Fail-closed protocol preflight: PASS.
- Gate 0.5 evidence artifact: `gate05-freeze-audit-82fd49bd3b91edf5ff9049b11f21dec02caa6e11`, artifact ID `10403037514`, archive SHA-256 `47e6611fda5d0510fb622594d92e535f90c1ab79ebbe0590f78bf72ad9a3229a`.

## Gate 0.4 evidence carried into freeze

Final scientific run: `34893947717`.

- canonical provenance round-trip: PASS
- completeness: PASS
- leakage audit: PASS
- downstream TRTR invariance: PASS
- generator seed uniqueness: PASS
- Gaussian Copula baseline: 10/10 unique full synthetic realisations
- TabDDPM algorithmic conformance: PASS

Validated artifacts:

- utility artifact ID `10370239011`, archive SHA-256 `09913fb3067aa792b537041c57c939fe53c34889f195e22392fdfeb0ec6d6492`
- full-realisations artifact ID `10369160706`, archive SHA-256 `103fe5da868e341620d715dcaa80b591ed121b0c536de50584c0393d558cb342`

## Freeze rule

No validated Core scientific implementation was changed to obtain the Gate 0.5 PASS. The post-CI repository change only changes the freeze candidate state to final frozen state and records Gate 0.5 evidence.

The following remain frozen against external-outcome-driven modification: generator families and frozen hyperparameters; leakage rules; deterministic seed policy; downstream seed comparability; CV/utility definitions; primary metrics; ICD component logic and primary lambda; DCR diagnostic-only role; provenance contract; and failure logging policy.

## External validation firewall and next authorized step

External confirmatory synthetic execution is now permitted **only after** the external dataset adapter and reference-effect/fingerprint definitions are preregistered without looking at PEERFIX synthetic outcomes. External results may not be used to retune the frozen Core.

The next authorized phase is therefore adapter/fingerprint preregistration for a qualified external dataset, followed by confirmatory execution under the frozen PEERFIX-Core v1.0. Source/provenance work performed before freeze does not itself constitute confirmatory generator execution.
