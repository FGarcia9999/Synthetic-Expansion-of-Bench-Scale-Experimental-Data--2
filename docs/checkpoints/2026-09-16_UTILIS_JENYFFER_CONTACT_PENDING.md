# PEERFIX-EXT — Candida utilis / contato com Profa. Jenyffer

Date: 2026-09-16
Branch: `freeze/peerfix-core-v1.0-2026-09-15`
Status: AUTHOR CONTACT ACTIVE — CLARIFICATION AND AUTHORIZATION PENDING

## Contexto

Foi encaminhada solicitação à Profa. Jenyffer Medeiros Campos Guerra, autora correspondente e orientadora do trabalho de *Candida utilis*, pedindo: (i) autorização para uso do estudo/dados no programa PEERFIX; (ii) esclarecimento da correspondência correta entre X3 e X4 no delineamento/modelo publicado; e (iii) eventual acesso aos registros experimentais que originaram a Tabela 2, especialmente valores individuais de tensão superficial e índices de emulsificação.

A mensagem também deixou explícito que dados brutos eventualmente cedidos não seriam publicados no repositório aberto; seria mantido apenas hash SHA-256 para proveniência, salvo autorização específica em contrário.

## Resposta recebida

Em 16/09/2026, a Profa. Jenyffer respondeu de forma positiva ao contato e convidou Fernando a conversar diretamente por WhatsApp para tratar das dúvidas, informando estar temporariamente afastada em evento em Belo Horizonte.

A resposta demonstra disposição concreta para esclarecer o conjunto e discutir o uso, mas **não contém ainda autorização explícita para uso dos dados nem confirmação formal de que os dados brutos serão fornecidos**. Portanto, o estado de governança deve permanecer conservador até a conversa/registro subsequente.

## Estado científico/proveniência

- B0-SOURCE/PROV: `PENDING AUTHOR CLARIFICATION`.
- B0-SCHEMA: `PENDING` quanto à identificação X3/X4 e disponibilidade dos registros individuais.
- Uso do conjunto para modificar o PEERFIX-Core v1.0: **PROIBIDO**, pois o Core já está congelado após Gate 0.5.
- Uso permitido após autorização: validação externa pós-freeze por adapter pré-registrado, sem retuning do Core.
- Raw-data redistribution: não assumida; depende de autorização explícita.

## Pontos que devem ser confirmados na conversa

1. autorização explícita para análise computacional dos dados no PEERFIX;
2. identificação correta de X3 e X4 no modelo estatístico publicado;
3. disponibilidade e semântica dos valores individuais de tensão superficial e E24;
4. unidade experimental / natureza das réplicas e IDs disponíveis;
5. autorização ou não para redistribuição pública do arquivo bruto; na ausência, manter somente hash/proveniência.

## Consequência esperada

Se esses pontos forem resolvidos positivamente, o conjunto de *C. utilis* poderá ser qualificado como um segundo dataset externo independente para testar transportabilidade/robustez do PEERFIX-Core congelado. Ele não poderá ser usado para alterar regras, geradores, hiperparâmetros, thresholds ou métricas do Core já congelado.
