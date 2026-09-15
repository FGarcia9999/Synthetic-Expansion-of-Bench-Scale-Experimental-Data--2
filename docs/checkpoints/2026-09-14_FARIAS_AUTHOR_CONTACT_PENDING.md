# PEERFIX-EXT1 — Contato com Charles Farias

Date: 2026-09-14
Status: AUTHOR CLARIFICATION PENDING
Branch: `resume/gate0.4-clean-derivation-2026-09-13`

## Contexto

Foi encaminhado e-mail a Charles Farias, autor de Farias et al. (2021, PeerJ), solicitando autorização para uso dos dados publicados como conjunto experimental independente no programa PEERFIX e esclarecimentos sobre a semântica das cinco medições `SAMPLES 1–5` presentes nos seis arquivos suplementares XLSX.

O contato não altera o status científico atual do conjunto. Até resposta explícita do autor, permanece válida a auditoria `2026-09-13_Farias_Audit_Report.md`.

## Questões enviadas ao autor

1. O que representam exatamente `SAMPLES 1–5` em cada condição experimental: cinco cultivos/fermentações independentes ou medições técnicas/alíquotas/leituras repetidas de uma mesma unidade experimental?
2. Como as cinco medições se relacionam com os resultados descritos no artigo como triplicatas e, no caso do índice de emulsificação, com a menção a quatro experimentos?
3. Caso três das cinco medições tenham sido selecionadas para médias e desvios-padrão publicados, quais foram utilizadas e segundo qual critério? Houve exclusão de outliers?
4. Há possibilidade de disponibilização de dados brutos/planilhas experimentais adicionais?
5. Foi manifestado convite para colaboração/coautoria, condicionado à concordância do autor.

## Estado de proveniência enquanto aguardamos resposta

- `SAMPLES 1–5`: `measurement_repeat_unknown_independence`.
- Uso de `n=220` como observações iid: PROIBIDO.
- Uso seguro provisório: nível de condição agregada, conforme auditoria anterior.
- B0-SOURCE/PROV: CONDITIONAL PASS.
- B0-SCHEMA: CONDITIONAL PASS.
- External confirmatory execution: PROIBIDA antes do freeze final do PEERFIX-Core/Gate 0.5.

## Possíveis consequências da resposta

Se Charles confirmar que `SAMPLES 1–5` são unidades experimentais biologicamente independentes, reabrir o B0-SCHEMA e reavaliar a elegibilidade row-level com identificação explícita da unidade experimental. Se forem repetições técnicas ou alíquotas da mesma unidade, manter análise condition-level e impedir pseudorreplicação. Se a relação com as triplicatas/quatro experimentos permanecer irresolvida, conservar o conjunto como candidato secundário/proveniência-robustness e não como base confirmatória principal row-level.

Nenhuma decisão metodológica do PEERFIX-Core será alterada em função desta resposta; ela poderá apenas mudar a elegibilidade/adaptação do dataset externo após o freeze.
