# PEERFIX-EXT1 — Auditoria célula a célula de Farias et al. (2021)

## Escopo

Auditoria estrutural e aritmética dos seis arquivos XLSX suplementares enviados para o artigo de Farias et al. (2021), com congelamento de hashes, inspeção de fórmulas/células, reconstrução de médias e desvios-padrão e avaliação preliminar dos Gates B0-SOURCE/PROV e B0-SCHEMA.

**Observação importante de fonte:** o PDF enviado com o nome do artigo de Farias contém internamente o artigo *Candida utilis Biosurfactant from Licuri Oil: Influence of Culture Medium and Emulsion Stability in Food Applications* (Fermentation, 2025). Assim, a comparação artigo↔XLSX foi feita contra a versão oficial de Farias et al. (2021) disponível em PeerJ/PMC.

## Resultado executivo

- 6 XLSX, 8 planilhas internas, 709 células não vazias auditadas.
- 44 grupos condição–resposta.
- 220 medições brutas numéricas, sempre 5 valores por grupo.
- 32 grupos de tensão superficial, 6 de E24 e 6 de dispersão.
- s001–s005: 38/38 grupos com resumo por fórmula reconciliam exatamente com os valores brutos.
- s006: 6/6 resumos superiores são hardcoded; todos os DPs divergem do STDEV.S recalculado e 3/6 médias apresentam arredondamento divergente.
- Não foram encontrados macros, links externos, comentários, planilhas ocultas, linhas/colunas ocultas ou erros de fórmula em cache.
- **B0-SOURCE/PROV: CONDITIONAL PASS.** A origem documental é forte, mas a independência experimental das cinco linhas `SAMPLES 1–5` não é identificável.
- **B0-SCHEMA: CONDITIONAL PASS.** A estrutura é canonicalizável, porém não existem `run_id`, `batch_id`, `flask_id` ou indicação explícita de réplica experimental versus leitura técnica.
- **Uso das 220 linhas como observações iid: NÃO autorizado.** Para uso imediato, a unidade mínima segura é a condição agregada.

## Manifesto SHA-256

|ID|Arquivo|SHA-256|Criador|Última modificação por|
|---|---|---|---|---|
|s001|Removal of heavy oil from contaminated surfaces with a detergent formulation containing biosurfactants produced by Pseudomonas spp-peerj-09-12518-s001.xlsx|`259ae9b3cd43299c56cd47a3dd6b7eabe786698821d084f080e2571398d9d472`|Pedro Brasileiro|Charles B B Farias|
|s002|Removal of heavy oil from contaminated surfaces with a detergent formulation containing biosurfactants produced by Pseudomonas spp-peerj-09-12518-s002.xlsx|`6690d3d25dd386cfc8b0c7c1701ecd937e85a587aa2a0fe3321e7ba86476bfe1`|Pedro Brasileiro|Charles B B Farias|
|s003|Removal of heavy oil from contaminated surfaces with a detergent formulation containing biosurfactants produced by Pseudomonas spp-peerj-09-12518-s003.xlsx|`c5d37aa0c30eb6a2d20009b7b43dad3b1e982cd9b80f604b1946fefe1ab1552a`|Pedro Brasileiro|Charles B B Farias|
|s004|Removal of heavy oil from contaminated surfaces with a detergent formulation containing biosurfactants produced by Pseudomonas spp-peerj-09-12518-s004.xlsx|`fa6376b6225f5c4af7335cc970be1dcd6c1d0183b84ec633eb314f380432a123`|Pedro Brasileiro|Charles B B Farias|
|s005|Removal of heavy oil from contaminated surfaces with a detergent formulation containing biosurfactants produced by Pseudomonas spp-peerj-09-12518-s005.xlsx|`c64cfe5974b7ba6df88ba777cd8a76abbb8dd5babed9bea6a51556ddfea01958`|Pedro Brasileiro|Charles B B Farias|
|s006|Removal of heavy oil from contaminated surfaces with a detergent formulation containing biosurfactants produced by Pseudomonas spp-peerj-09-12518-s006.xlsx|`865c14deb649c064a025c41a6522adbd10bd289b23275e88144cdacdd7a8e332`|Pedro Brasileiro|Charles B B Farias|

## Estrutura experimental recuperada

|Arquivo|Bloco|Nº de condições|Leituras por condição|
|---|---:|---:|---:|
|s001|surface_tension|4|5|
|s002|surface_tension|6|5|
|s003|surface_tension|10|5|
|s004|surface_tension|12|5|
|s005|emulsification_E24|6|5|
|s006|motor_oil_dispersion|6|5|

## Inconsistência crítica de replicação

Os seis workbooks apresentam cinco linhas de medição em **todos** os 44 grupos. Entretanto, as legendas das Figuras 2–6 do artigo descrevem resultados como médias de experimentos em triplicata; no método do E24 há ainda menção a quatro experimentos. Como os XLSX não fornecem IDs hierárquicos, não é possível determinar se as cinco linhas são fermentações independentes, tubos independentes, leituras instrumentais repetidas ou outra combinação. Portanto, elas não podem ser tratadas como cinco unidades experimentais independentes.

## s006 — dispersão: reconciliação dos resumos hardcoded

|Organismo|Razão|Média raw|Média resumo|DP raw|DP resumo|
|---|---:|---:|---:|---:|---:|
|P. aeruginosa ATCC 10145|1:2|99.2200|99.2200|0.4645|0.5000|
|P. aeruginosa ATCC 9027|1:2|66.2400|66.2400|0.7403|0.7000|
|P. aeruginosa ATCC 10145|1:8|74.9120|75.0000|1.8217|2.0000|
|P. aeruginosa ATCC 9027|1:8|62.1600|62.0000|1.5192|2.0000|
|P. aeruginosa ATCC 10145|1:25|79.3000|79.3000|2.9069|3.3800|
|P. aeruginosa ATCC 9027|1:25|64.8000|65.0000|1.6808|2.0000|

Os valores superiores de s006 devem ser ignorados na canonicalização; médias e DPs devem ser recalculados diretamente das cinco medições originais e a divergência preservada no log de auditoria.

## Consequência para o PEERFIX

### Uso row-level
Bloqueado até que a natureza das cinco linhas seja esclarecida. Contá-las como `n=220` produziria pseudorreplicação potencial.

### Uso condition-level
É defensável construir uma base de condições agregadas, mantendo cada combinação experimental como unidade: 32 condições para tensão superficial, 6 para E24 e 6 para dispersão. Isso permite concordância de domínio e, de forma condicional, validação preditiva agrupada, mas **não** transforma os cinco valores por condição em réplicas biológicas.

### Adequação como Manuscrito 2
O conjunto é melhor do que PEERFIX3-Yali em disponibilidade documental, porém a auditoria reduz a avaliação de 'alta viabilidade confirmatória' para **viabilidade moderada/condicional**. Ele é um bom candidato a external-dataset transportability em nível de condição, mas ainda não é uma base limpa para validar modelos usando as 220 linhas individualmente.

## Decisão recomendada

1. Preservar os seis XLSX originais imutáveis e seus hashes.
2. Criar um `canonical_condition_level.csv` com uma linha por condição e estatísticas recalculadas.
3. Classificar `SAMPLES 1–5` como `measurement_repeat_unknown_independence`, não como réplica experimental.
4. Não usar `n=220` em nenhuma análise de utilidade.
5. Para Manuscrito 2, comparar formalmente este conjunto com o CCRD de 27 runs de *Candida mogii* e o fatorial de 19 runs de *Candida utilis* antes de escolher a base externa definitiva.
6. Se for desejado usar o nível bruto de Farias et al., a única pendência autoral realmente crítica é explicar a semântica das cinco linhas por condição e a discrepância triplicata/quatro experimentos/cinco medições.
