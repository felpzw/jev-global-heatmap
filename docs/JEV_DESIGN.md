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
