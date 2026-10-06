> Snapshot histórico substituído pela [ADR 0003](../adr/0003-affinity-ranking.md) em 05/10/2026. Planos e estados abaixo descrevem a decisão anterior.

# Desenho da JEV sem LLM

Estado: arquitetura-alvo definida em 05/10/2026; implementação pendente.
Substitui a proposta JEV baseada em geração de linguagem, preservada em legacy.

## Dados e fontes

Avaliar Wikipedia por API MediaWiki, Wikidata por API/SPARQL/recorte de dump,
APIs oficiais por domínio e dataset local CSV/JSON/Parquet. Wikipedia fornece
conteúdo; tabelas/textos precisam de extração e validação específica. Wikidata
oferece dados estruturados, cuja pertinência, referências e tempo precisam ser
verificados. Nenhuma fonte garante cobertura ou histórico suficientes aos 195.

Preferir aquisição reproduzível com snapshot local para o primeiro ensaio;
a escolha definitiva depende da issue de dados. Comparar arquivos/manifestos,
SQLite e DuckDB antes de introduzir banco servidor. Banco armazena informações;
não substitui fonte, normalização ou estimador.

Referências: [MediaWiki REST API](https://www.mediawiki.org/wiki/API:REST_API),
[acesso Wikidata](https://www.wikidata.org/wiki/Wikidata:Data_access),
[SPARQL](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service),
[Banco Mundial](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392).

## Contratos propostos

| Estrutura | Conteúdo mínimo |
| --- | --- |
| ForecastRequest | domínio/evento suportado, contexto opcional, indicador/unidade/limiar, deadline, resolution_rule, as_of, modo e versão de dados, método |
| Observation/Evidence | id, países, indicador/valor/unidade ou material extraído, origem/URL/arquivo, referência temporal, publicação/coleta, revisão/versão, hash, transformação |
| CountryForecast | ISO alpha-3, probability, status, rationale por template, ids de dados, método e calibration_status |
| ForecastResponse | schema_version, run_id, pedido original, versão do registro/dataset, catálogo de dados, estimador/parâmetros/versão, estado/tempos/falhas e countries |

Metadados de provedor LLM/modelo/prompt não são obrigatórios no contrato novo.
Lote e resposta final têm validações diferentes: lote cobre seu subconjunto;
resultado final exige igualdade exata com o registro dos 195, não só comprimento.
M49 é string de três caracteres. Registro e código não são inventados por modelo.

estimated exige número finito em [0,1]. insufficient_evidence, not_applicable
ou error exigem null; cada estado tem justificativa. Não confundir execução
completa e ausência de erros técnicos; abstenções podem fazer parte de uma execução
concluída. Chaves extras, tipos indevidos, duplicatas, IDs inexistentes ou dados
inadequados ao país/evento são rejeitados. Probabilidades não precisam somar 1.

## Catálogo e significado dos valores

O catálogo versionado define `event_id`, domínio, indicador, unidade, operador
permitido para o limiar, regra de resolução, fontes compatíveis e métodos
admitidos com seus pré-requisitos. `ForecastRequest` identifica `event_id` e
`catalog_version`, além dos campos acima. O catálogo nasce da seleção em #13,
seu contrato é implementado em #14 e sua apresentação em #16. Não há evento
universal, extração automática de intenção ou seleção silenciosa por texto livre.
O serviço rejeita incompatibilidades de evento, unidade, fonte, método ou versão
antes de adquirir dados. Para previsão futura, `deadline` deve ser posterior
a `as_of`; a regra de resolução precisa definir como o desfecho será observado.

| Tipo | Significado | Uso no resultado |
| --- | --- | --- |
| Observação | Valor de um indicador em unidade e período definidos, com proveniência | Entrada rastreável do estimador; não preenche `probability` diretamente |
| Score por regras | Índice calculado por uma regra e escala explícitas | Identificado separadamente; não convertido em probabilidade por normalização |
| Probabilidade | P(evento no país até deadline condicionado aos dados disponíveis em as_of) | `probability` em [0,1] somente com método probabilístico identificado |

`calibration_status` distingue ausência de avaliação de evidência de calibração;
`estimated` apenas indica que houve uma estimativa. Não implica calibração nem
precisão factual comprovada. O `heat_score` Gemini continua no contrato legado.

## Estado da execução e reconciliação

A resposta final contém exatamente o conjunto do registro, mesmo com abstenções.
`completed` admite `insufficient_evidence` e `not_applicable`; qualquer `error`
técnico por país torna a execução `partial`. A justificativa explica cada status,
e a ausência de dados nunca gera probabilidade zero.

Progresso, falha anterior à estimação e cancelamento são estados de execução,
não previsões concluídas. Checkpoints podem conter subconjuntos e não são
exportados como resposta final reconciliada. A UI mantém o resultado anterior
com seu `run_id` separado. O contrato de execução em #14 e o motor em #15
formalizam essas transições e os campos de erro; retomada respeita pedido,
registro, catálogo, snapshots e versões originais.

## Estimador e planejamento

A JEV seleciona conectores e métodos por configuração/catálogo, organiza consultas,
normaliza unidades/datas e aplica corte temporal. Não interpreta qualquer texto
livre como evento executável. Evento ambíguo, não suportado ou com prazo inválido
retorna orientação antes de estimar.

A escolha do estimador depende do primeiro domínio e seus dados. Candidatos são
baseline de taxa-base, modelos de séries temporais/simulações para ultrapassagem
de limiar ou classificação probabilística com desfechos históricos. Uma regra
que gera score não pode preencher probability sem método probabilístico validado.
Ausência de dados retorna abstenção; prior só entra com política explícita.

## Execução e rastreabilidade

Definir timeout/retry, concorrência, lotes quando necessários e limite de consultas
antes do ensaio integrado. Cache identifica pedido, as_of, país, fonte/revisão,
registro, dataset, transformação e estimador/parâmetros. Definir validade/retenção
e isolamento por sessão. Checkpoints locais têm gravação atômica e run_id.
Retomada usa os mesmos snapshots; alteração de dados implica nova execução.

Dados externos precisam de data/versão verificável. Revisão de página e data de
coleta não substituem a data do indicador nem comprovam disponibilidade em as_of.
Explicações usam templates e identificam valores, método e fontes sem chamada LLM.

## Produto e avaliação

Mapa percentual apenas para estimated; nulos/status próprios, países fora do
escopo distintos, tabela/busca para todos e microestados. JSON preserva toda
proveniência. Resultado anterior é mantido separado após falha/cancelamento.
O legado qualitativo fica identificado durante a migração.

Definir baseline, desfechos, separação temporal, limiares e amostra antes de testar.
Avaliar Brier, log loss, curvas de confiabilidade, cobertura/abstenções/erros e
incerteza; considerar dependência entre países/eventos. Arquivar previsões
prospectivas. Estimador permanece não calibrado até evidência fora da amostra.
Benchmark mede p50/p95, recursos e consultas com/sem cache no mesmo workload.
JSON válido e extração correta não comprovam desempenho preditivo.

## Rastreabilidade das entregas

A [ADR 0002](../adr/0002-jev-without-llm.md) rege este desenho; a
[arquitetura](ARCHITECTURE_NO_LLM.md) define responsabilidades e dependências.
O [plano ativo](JEV_IMPLEMENTATION_PLAN_NO_LLM.md) liga os contratos às issues
#13–#17. O [MVP](../MVP_LEGACY.md) e os [snapshots com LLM](README.md)
descrevem o código e a proposta anteriores, sem atribuir execução à JEV.
