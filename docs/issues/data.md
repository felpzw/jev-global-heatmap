# Dados: avaliar Wikipedia/Wikidata, APIs e datasets locais para a JEV

Issue: [13](https://github.com/felpzw/jev-global-heatmap/issues/13).
## Objetivo e entregas

Selecionar fontes, estratégia de aquisição e armazenamento para a JEV sem LLM. Não pré-selecionar banco ou fonte.

## Alternativas
Wikipedia via API MediaWiki (conteúdo/tabelas/revisões), Wikidata via API/SPARQL ou recorte de dump (dados estruturados/qualificadores/referências), APIs oficiais por domínio e dataset local CSV/JSON/Parquet. Comparar arquivos/manifestos, SQLite e DuckDB; banco servidor somente com necessidade demonstrada.

## Atividades
- [ ] Escolher domínio inicial, evento observável, indicador/unidade/limiar/prazo e fontes pertinentes.
- [ ] Comparar cobertura dos 195, histórico, atualização, qualidade, revisões, licença/atribuição, limites de chamadas, custo e reprodução.
- [ ] Fazer prova de conceito de aquisição externa e leitura local equivalentes, sem LLM nem download indiscriminado de dumps completos.
- [ ] Normalizar país ISO alpha-3, indicador, valor, unidade, período e missing data; distinguir territórios fora do escopo.
- [ ] Registrar URL/arquivo, revisão/versão, publicação/coleta/referência temporal, hash e transformação.
- [ ] Avaliar snapshots para as_of; data de revisão de página não comprova disponibilidade histórica de toda afirmação.
- [ ] Definir cache/atualização, timeout/retry, limites, armazenamento bruto/normalizado, manifestos, retenção e local_only sem rede.
- [ ] Documentar fonte principal e fallback explícito, lacunas e decisão de armazenamento.

## Aceite
Matriz comparativa, ADR da seleção e amostra reproduzível com proveniência/relatório de cobertura. Ausência de dados explícita, sem inventar valores. Não exige 195 valores válidos nem previsão. Investigação pode começar com a fundação em andamento; integração depende dos contratos geográficos.

## Referências oficiais
- https://www.mediawiki.org/wiki/API:REST_API
- https://www.wikidata.org/wiki/Wikidata:Data_access
- https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service
- https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
