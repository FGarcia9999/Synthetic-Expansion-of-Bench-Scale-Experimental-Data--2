# PEERFIX Scientific Charter — Core v1.0

Status: Gate 0.5 freeze candidate
Date: 2026-09-15

## Purpose

PEERFIX is a framework for trustworthy synthetic augmentation of small experimental-science datasets. Its purpose is not to manufacture evidence, increase nominal biological sample size, or guarantee predictive improvement. It tests whether synthetic generation preserves scientifically relevant structure while maintaining strict provenance, leakage control, modelability checks, and transparent failure modes.

## Scientific program

1. Development/derivation: PEERFIX2.
2. Transportability: post-freeze external datasets.
3. Robustness/modelability/provenance stress: structurally difficult or partially ineligible datasets.

## Core principle

Synthetic rows are computational objects. They are never treated as new biological experiments or independent experimental replicates.

## Modelability gate

A block is eligible for synthetic modeling only when all four conditions pass:

- source/provenance is traceable;
- experimental unit is defined;
- support is sufficient for the requested analysis;
- the scientific relation being evaluated is identifiable.

Failure of any component prohibits synthetic modeling for that block. Descriptive/provenance analysis may remain permissible.

## Frozen Core invariants

After Gate 0.5, external outcomes may not change:

- generator families and frozen hyperparameters;
- leakage rules;
- deterministic seed policy;
- downstream seed comparability across generator labels;
- TRTR/TSTR/AUGTR definitions;
- primary repeated-CV geometry and reporting logic;
- ICD matched-effective-n logic and primary lambda;
- failure logging/fail-closed behavior;
- DCR diagnostic-only policy;
- canonical persistence/hashing contract;
- rule that target responses are not clipped to observed training range unless a domain adapter preregisters a genuine physical bound.

## Adapter freedom

Before viewing external synthetic outcomes, a dataset adapter may define:

- source identity and raw-file hashes;
- canonical column mapping and units;
- experimental unit;
- grouping/pairing keys;
- factor/response roles;
- declared design support and physical constraints;
- CV geometry required by the design;
- domain reference relations/effect fingerprints;
- block-level modelability eligibility.

These decisions must be preregistered before any external generator execution.

## Evaluation domains

PEERFIX deliberately separates:

- predictive transport/utility;
- fidelity to marginal and multivariate structure;
- DOE/design-support preservation;
- domain-effect concordance (ICD);
- proximity diagnostics (DCR);
- provenance/reproducibility.

No single metric defines success and no generator is selected as universally best from one criterion.

## Negative results

A conformant generator that performs poorly is a valid scientific result. It must not be tuned away after outcomes are observed. Gate 0.4 demonstrated this explicitly for the frozen small-n TabDDPM configuration.

## Derivation firewall

The derivation dataset is the source-confirmed 20-run PEERFIX2 dataset from Souza (2009), SHA-256 `c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07`.

The cleanup-substituted dataset SHA-256 `d7420eaa5d1c45f1287e12af5737893b244a6302beecab0da35a2b464d040001` is prohibited for derivation and external confirmation.

## External firewall

External datasets may be source/provenance audited before freeze but may not be used to tune Core algorithms, thresholds, generator settings, seeds, primary metrics, or reference-effect rules. Confirmatory generator execution begins only after Gate 0.5 PASS and a preregistered adapter/protocol.

## Manuscript interpretation rule

Claims must distinguish relative stabilization from absolute modelability. A positive TSTR−TRTR delta does not by itself establish adequate predictive performance when TSTR remains poor. Synthetic augmentation is not evidence-equivalent to new experiments.
