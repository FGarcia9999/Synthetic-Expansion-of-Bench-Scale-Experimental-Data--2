# PEERFIX EXT-D — Farias adapter compatibility gate

Date: 2026-09-22
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`
M2 scientific freeze checkpoint: `docs/checkpoints/2026-09-22_MANUSCRIPT2_SCIENTIFIC_FREEZE.md`

## Context

Condition-level recanonicalization and pre-generation modelability screening identified the following Farias blocks:

- `P. aeruginosa UCP0992` surface tension: PASS modelability; preferred prospective block.
- `P. aeruginosa ATCC10145` surface tension: PASS modelability; strong secondary block.
- `P. cepacia CCT6659` surface tension: conditional.
- `P. aeruginosa ATCC9027` surface tension: borderline/conditional.
- E24 and motor-oil dispersion: blocked by modelability.

No synthetic generation has been executed for EXT-D.

## Adapter representability audit

The frozen external runner currently assumes that every declared factor column is numeric. Its `_support` routine coerces factors with `pd.to_numeric`, and the frozen generator metadata declares every input column as numerical. Generator output is then snapped independently, column by column, to the declared numeric support.

This is compatible with the numerical/coded DoE factors used by EXT-A (`C. mogii`) and EXT-B (`C. utilis`).

The Farias experiment differs materially. Its main design factor is `production medium`, a categorical formulation factor:

### UCP0992

Five media:
- glucose 1.5%
- glucose 2.0%
- glucose 3.0%
- sucrose 2.0%
- sucrose 3.0%

crossed with two temperatures (28 and 37 °C).

### ATCC blocks

Three distinct media formulations crossed with two temperatures (28/35 °C).

## Why naive encoding is not authorized

### Integer coding

Mapping media to arbitrary values such as `0,1,2,3,4` would impose an artificial ordinal/metric distance among qualitatively different formulations. That changes the scientific geometry of the experiment and is not a neutral adapter operation.

### Independent one-hot columns

One-hot encoding would preserve categorical meaning for regression, but the current frozen generator/snap logic treats each factor column independently. Synthetic rows could therefore contain invalid multi-hot or all-zero combinations unless a joint categorical constraint/projection rule were added.

Adding such a projection or joint-support constraint after seeing the EXT-D design would be a new post-freeze behavior and is therefore not authorized as a silent change to PEERFIX-Core v1.0.

### Carbon-family + concentration decomposition

Representing medium as `carbon_family` plus `concentration` is also not equivalent to the source design. UCP0992 does not contain a complete family × concentration factorial (sucrose 1.5% is absent), and the medium factor in the source experiment is the formulation itself. Decomposition would therefore introduce untested combinations and a different model geometry.

## Gate decision

- Source provenance: PASS.
- Condition-level canonicalization: PASS.
- Source modelability for UCP0992: PASS.
- Scientific relation identifiability: PASS at condition level.
- **Frozen-Core adapter representability: FAIL / BLOCKED.**

### Formal status

`BLOCKED_BY_ADAPTER_REPRESENTABILITY`

This is not a biological/modelability failure. It is a transportability limitation of the frozen numerical-factor interface.

## Consequence

No EXT-D synthetic generation is authorized on the current frozen Core.

The Farias dataset remains scientifically valuable as a post-M2 stress test because it exposes a new boundary condition: a method developed around coded/numerical DoE factors cannot automatically be extended to nominal formulation factors without an explicit categorical-design policy.

## Future route

A future PEERFIX-Core v1.1 or separate extension may add preregistered categorical-factor support, including joint-validity constraints for synthetic design points. Such work must be treated as method development, not as a retuning of Core v1.0 to obtain a favorable Farias result.

EXT-D results must not be back-propagated into M2.

## Core status

No PEERFIX-Core v1.0 file, generator, seed, threshold, metric, ICD rule or existing EXT-A/EXT-B adapter was changed.