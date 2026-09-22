# PEERFIX EXT-C — prospective Fontes outcome

Date: 2026-09-22  
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`  
Frozen Core anchor: `0d5a73d128fe374c8165f3b84a2412ac9b02cbc1`  
Execution authorization commit: `7db48d2563d0b650b96629b75d0ece1a5ebac30f`  
GitHub Actions run: `35762906755` — **completed / success**

## Scope

This checkpoint records the first prospective post-freeze EXT-C execution using Fontes et al. (2010), Table 4, exactly as preregistered. No PEERFIX-Core v1.0 file, generator family, random seed, threshold, ICD rule, validation geometry, downstream model panel, or decision rule was retuned after observing the outcome.

Canonical source table SHA-256: `41dba19fe743147ab249951c2e388a2f6c0647fa55af7b306e7fe54223f2f5d2`.

## Integrity audit

- EI block: **1030 checks PASS, 0 failures**.
- delta-ST block: **1030 checks PASS, 0 failures**.
- Four generators retained: Gaussian Copula, CTGAN, TVAE and TabDDPM.
- Both validation geometries retained: experiment-wise and grouped-condition.
- Synthetic sample size: 140, as frozen.
- No outcome-driven rerun, exclusion or generator-specific optimization was used.

Audit PASS means execution/integrity conformance. Scientific transportability is interpreted from the frozen metrics.

## Primary result — EI

TVAE is the only generator with positive synthetic-to-real predictive performance in both validation geometries under the primary linear-regression reference:

- experiment-wise: TRTR R2 = **0.224**, TSTR R2 = **0.186**, delta = **-0.037**;
- grouped-condition: TRTR R2 = **0.080**, TSTR R2 = **0.134**, delta = **+0.054**.

Across the ten preregistered repeats, TSTR R2 was positive in 9/10 experiment-wise repeats and 8/10 grouped-condition repeats. The mean TSTR R2 was positive under both geometries.

Interpretation: **POSITIVE SELECTIVE PREDICTIVE TRANSPORT**. This is a second prospective predictive-positive case after C. mogii. The absolute magnitude is modest, so it must not be described as strong universal prediction or global synthetic-data validation. Its scientific strength is the prospective, leakage-controlled reproduction of positive synthetic-to-real predictive signal in a distinct experiment.

Gaussian Copula was positive only experiment-wise for EI (TSTR R2 = 0.099) and negative under grouped-condition validation. CTGAN and TabDDPM were negative.

## Secondary result — delta-ST

TVAE again produced positive absolute TSTR performance in both geometries:

- experiment-wise: TRTR R2 = **0.323**, TSTR R2 = **0.199**, delta = **-0.123**;
- grouped-condition: TRTR R2 = **0.279**, TSTR R2 = **0.137**, delta = **-0.142**.

Interpretation: **PARTIAL PREDICTIVE TRANSPORT**. The synthetic-only model retains real held-out predictive signal, but the loss relative to TRTR is systematic. This response is not the main second positive-parity case.

## Multi-objective result

EXT-C reinforces the need to separate predictive transport from structural fidelity/concordance.

For delta-ST, Gaussian Copula had the strongest structural diagnostics among the panel (mean ICD approximately **0.387**, correlation-of-correlations approximately **0.942**, DOE cell coverage approximately **0.929**) while TSTR R2 remained negative. TVAE had lower structural scores but retained positive predictive utility.

Therefore, fidelity/concordance and predictive transport remain distinct objectives. No generator is globally superior across all axes.

## Negative evidence retained

- CTGAN: negative TSTR for EI and delta-ST in both validation geometries.
- TabDDPM: strongly negative TSTR under the frozen small-n configuration.

These outcomes remain part of the evidence chain. They were not removed or tuned away.

## Relationship to Farias EXT-D

Farias remains complementary evidence of `BLOCKED_BY_ADAPTER_REPRESENTABILITY`: a scientifically modelable response can still be correctly blocked if the frozen v1.0 representation would distort a nominal experimental factor. EXT-C and EXT-D therefore test different properties of the same fail-closed protocol.

## Scientific decision

EXT-C closes with the following outcome classes:

1. **EI + TVAE:** positive selective predictive transport — second prospective predictive-positive case.
2. **delta-ST + TVAE:** partial predictive transport.
3. **Gaussian Copula:** stronger structural fidelity/concordance but no consistent predictive transport in EXT-C.
4. **CTGAN:** negative external result.
5. **TabDDPM:** strongly negative external result.

This outcome supports PEERFIX-Core v1.0 as a selective decision protocol, not as a guarantee that synthetic expansion will improve every experiment or every generator.

No further retuning of PEERFIX-Core v1.0 is authorized from these outcomes. Any categorical-factor support or other methodological extension belongs to a separately versioned future Core.

## Local evaluation artifact

`PEERFIX_EXTC_Fontes_Final_Evaluation_v1.xlsx`  
SHA-256: `e16d35d33de253ec6ca0e24e6ace0042ef8b3a6fd315641b929b31aa98ad256f`
