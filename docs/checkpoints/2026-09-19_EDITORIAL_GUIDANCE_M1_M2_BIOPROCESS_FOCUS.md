# PEERFIX editorial guidance for next manuscript revision — bioprocess focus

Date: 2026-09-19
Branch: `external/peerfix-ext-mogii-utilis-2026-09-16`
Status: accepted editorial guidance with scientific safeguards
Source reviewed: `Blocos_Discussao_M1_M2_ganho_bioprocesso_1.docx`

## Purpose

Preserve the proposed experimental/bioprocess framing for the next revision of Manuscripts 1 and 2 while preventing claims that exceed the frozen PEERFIX-Core v1.0 evidence.

## Accepted editorial principles

1. Prefer short sentences and experimental language before computational jargon.
2. Organize Discussion as: observed experimental result -> meaning for bioprocess decisions -> supporting metric -> literature.
3. Emphasize tension surface, medium composition, factor-response relations, emulsification, design geometry, experimental variability and need for new bench runs.
4. Treat synthetic expansion as exploratory support and prioritization aid, never as a substitute for biological replication.
5. In M2, explicitly cross-reference M1 so that the dissociation between fidelity, predictive utility and effect preservation is inherited from the development paper rather than re-demonstrated; this reduces fragmentation/salami risk.
6. Keep external validation focused on transportability of a frozen protocol, not on new method development.

## Manuscript 1 — accepted with wording safeguards

The proposed 'ganho para o bioprocesso' block is conceptually appropriate. It should state that the C. lipolytica experiment supports a reproducible negative KH2PO4 effect while the 20-run dataset does not support strong individual prediction. Synthetic data can be described as useful for checking stability of this relation and for exploratory prioritization within the studied experimental domain.

Required safeguard: do not claim that PEERFIX identifies the optimal next fermentation conditions or performs optimal experimental design. Replace strong language such as 'decidir onde investir novas fermentações' by 'ajudar a priorizar quais relações e regiões do domínio merecem confirmação em novas fermentações'.

## Manuscript 2 — accepted with wording safeguards

The proposed bioprocess paragraph is strong and should be incorporated, but the positive C. mogii statement must be generator-specific. Use language such as: 'com a Cópula Gaussiana, os dados sintéticos preservaram capacidade preditiva próxima à obtida apenas com as corridas reais'. Do not generalize this result to synthetic expansion as a whole because TVAE only partially transported and CTGAN/TabDDPM did not.

For C. utilis Y2, retain the practical interpretation that the unsupported motor-oil emulsification response was blocked before synthetic generation. This is a scientifically useful fail-closed result.

Required safeguard: exploratory use of synthetic data must always be described as preceding or supporting new bench work, not eliminating the need for confirmatory fermentations.

## Anti-salami cross-reference

Accepted. The preferred M2 framing is:

'A dissociação entre fidelidade estatística, utilidade preditiva e preservação dos efeitos experimentais foi estabelecida no estudo de desenvolvimento do PEERFIX-Core v1.0 [estado real do M1] e é aqui assumida como premissa. O presente trabalho pergunta se o protocolo, congelado antes do contato com os dados externos, mantém essa avaliação em experimentos independentes.'

At M2 submission, replace the M1 placeholder with the actual status: in preparation, submitted, accepted/in press, or DOI.

## Important scientific correction to the proposed M1 conclusion

Do NOT state that low ICD detectability proves that the original experiment is 'subdimensionado' or that PEERFIX directly identifies where the next runs should be placed. The matched-n detectability component describes how often the effect remains statistically detectable in synthetic subsamples; it is not a formal prospective power analysis or an optimal-design calculation.

Safer formulation:

'Quando sinal e magnitude são preservados, mas a detectabilidade permanece baixa, a expansão indica que a relação merece confirmação adicional em novas corridas. A localização e o número dessas novas corridas devem ser definidos por um novo planejamento experimental, não pelo gerador sintético isoladamente.'

The exact S/M/D percentages must be rechecked against the final Supplementary before insertion.

## Conclusion framing

Accepted practical message for both papers: the main value of PEERFIX is not multiplying observations but separating three decisions:
- what relation is already supported by the experiment;
- what relation can be explored synthetically without changing its scientific meaning;
- what relation still requires additional bench evidence.

This should be the dominant bioprocess interpretation in the next manuscript revision.

## References

Helleckes et al. may serve as the direct bioprocess/ML anchor. SynthEval and Nanevski should be used only as methodological/adjacent-domain support after the experimental interpretation. Their exact claims and bibliographic details must be verified before final submission.

## Next-revision rule

Apply this guidance at the next M1/M2 edit. Do not modify frozen PEERFIX-Core v1.0 or reinterpret confirmatory results. This checkpoint is editorial only.
