# PEERFIX Dataset Adapter Specification v1.0

Status: freeze candidate

A dataset adapter maps one external experimental dataset into the frozen PEERFIX-Core without changing Core scientific decisions.

## Required adapter fields

### Identity and provenance
- adapter id/version;
- study citation;
- raw source location/status;
- raw-file SHA-256 values;
- authorization/redistribution status;
- canonical dataset SHA-256;
- canonicalization log.

### Experimental structure
- experimental unit definition;
- n independent experimental units;
- replicate hierarchy (biological/experimental/technical/measurement);
- run/batch/flask/group identifiers when available;
- DOE/design family;
- factor list, roles, units, coded/real mappings;
- response list, roles, units;
- center/axial/factorial/block information when applicable.

### Modelability gate
Each requested modeling block must declare PASS/FAIL for:
- source traceability;
- experimental-unit definition;
- support sufficiency;
- reference-relation identifiability.

A single FAIL blocks synthetic modeling for that block.

### Constraints
Before outcome inspection, declare:
- designed factor support;
- physical/domain bounds if genuinely known;
- whether snapping to designed factor levels is appropriate;
- forbidden/impossible combinations;
- response hard bounds only when independently justified.

Observed training minima/maxima are not automatically physical response bounds.

### Validation geometry
Declare before generator execution:
- row-level or grouped split unit;
- required grouping/pairing keys;
- treatment of center replicates;
- folds/repeats compatible with design support.

The adapter may require a stricter structural CV than the generic row CV but may not loosen leakage protection.

### Domain reference relations
Before external synthetic generation, freeze:
- primary confirmed effects/relations;
- effect direction where applicable;
- source of confirmation;
- secondary/borderline relations, clearly separated from primary relations.

The reference set may not be changed because synthetic results are favorable or unfavorable.

## Output contract

The adapter must expose a `BlockSpec`-equivalent structure containing factors, responses, experimental unit, grouping, constraints and validation geometry. The Core must remain unaware of organism-specific naming beyond the adapter mapping.

## Pseudoreplication rule

Technical readings or within-run replicate measurements may be used to estimate measurement variability or construct run-level responses, but they may not be promoted to independent experimental units without source-supported independence.

## Current candidate examples

### Candida mogii / Peterson-Jenyffer
- experimental unit: DOE run;
- n=27;
- design: four-factor CCD/response-surface design, alpha=2;
- primary response candidate: STred;
- ST1–ST3: within-run readings, not independent DOE rows;
- source/provenance: PASS;
- schema: PASS at run level.

### Farias et al. 2021
- `SAMPLES 1–5`: currently `measurement_repeat_unknown_independence`;
- row-level use blocked pending author clarification;
- condition-level aggregation remains the safe provisional representation.
