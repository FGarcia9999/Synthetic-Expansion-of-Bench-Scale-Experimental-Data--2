# PEERFIX external validation — start checkpoint

Date: 2026-09-16
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
External branch: `external/peerfix-ext-mogii-utilis-2026-09-16`

## Decision

The post-freeze external-validation phase is authorized to proceed with two author-supplied datasets while the Farias clarification remains pending.

- **EXT-A / C. mogii**: primary transportability validation, 27-run CCD, canonical response `STred`, source/model reconstruction already audited.
- **EXT-B / C. utilis**: second independent external challenge, 19-run full 2^4 + 3 centers, response-specific gates for Y1/Y2/Y3; X3/X4 ambiguity resolved by original Protimiza matrix and coauthor clarification.
- **Farias et al.**: remains held out; no row-level external execution until `SAMPLES 1–5` independence is clarified.

The frozen Core itself is not modified. The external adapters and confirmatory order were committed before any generator execution. Raw author-supplied workbooks remain outside the public repository unless separate public-redistribution permission is documented.

## GitHub Actions / billing discipline

External preregistration is performed on a branch not targeted by the completed Gate 0.4 or Gate 0.5 push workflows. Scientific external execution should be triggered deliberately, not by documentation-only commits. This avoids unnecessary Actions runs while preserving the frozen Core branch as an audit anchor.

## Next implementation step

Create a fail-closed external runner that consumes the frozen Core plus an adapter, verifies the local/private workbook SHA-256, materializes a canonical run-level table in the execution workspace, and executes EXT-A first and EXT-B second without retuning. No Farias execution is authorized yet.
