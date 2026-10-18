# Dados: catálogo de critérios e dataset de afinidade por país

Issue: [13](https://github.com/felpzw/jev-global-heatmap/issues/13).

## Objetivo

Selecionar critérios mensuráveis e evidências para ranking de afinidade com o
pedido, conforme ADR 0003. Revisão do escopo anterior de previsão sem LLM;
não declara concluída a investigação anterior. Pode avançar com #14.

## Entregas

- [x] Catálogo inicial pequeno para praia e idioma: definições, sinônimos, tipos, unidades, operadores e ambiguidades; distinguir litoral/praia turística e inglês oficial/proficiência.
- [x] Fontes pertinentes e licenciadas: comparar Wikidata, Wikipedia, fontes oficiais e datasets locais por cobertura dos 195, qualidade, atualização e reprodução.
- [x] Dataset local versionado com manifestos e amostra reproduzível; aquisição sem LLM, sem obrigar banco servidor ou consulta online durante ranking.
- [x] Normalização por ISO alpha-3, atributo, valor/unidade e período; ausência de dados explícita, sem completar com conhecimento da LLM.
- [x] Proveniência por evidência: URL/arquivo, publicação/coleta, revisão/versão, hash e transformação; relatório de cobertura por critério/país.
- [x] Definir normalização para [0,1], requisitos e preferências, política de missing data, atualizações, retenção e limites de aquisição.
- [x] Registrar seleção em ADR de dados; justificar armazenamento e eventuais conectores externos, sem downloads indiscriminados.

## Aceite

Catálogo, dataset/amostra e matriz de fontes reproduzíveis, com licença,
proveniência e lacunas. Não exige dados válidos para todos os países, previsão
ou LLM. Dados de país não garantem condições de cada cidade/região. Integração
com #15 depende dos contratos de #14.

## Investigação iniciada em 05/10/2026

[Pesquisa de dados](../DATA_RESEARCH.md): comparação de JSON/JSONL, CSV,
SQLite e Parquet/DuckDB; matriz de fontes, modelo lógico, aquisição limitada,
manutenção, retenção e roteiro do primeiro piloto.

[ADR 0004](../adr/0004-local-affinity-data.md) registra a recomendação provisória
de snapshots JSON/JSONL. A decisão depende do piloto e do alinhamento com #14.
A pesquisa inicial foi preservada. O piloto posterior adquiriu o arquivo
Factbook e publicou o snapshot; fontes e cobertura atuais estão no relatório de entrega.

## Evidências de implementação em 18/10/2026

Consulte [DELIVERY.md](../DELIVERY.md), [fontes e reprodução](../../data/SOURCES.md)
e a suíte offline. Integração destinada à `develop`; a PR registra o estado remoto.
O snapshot é histórico; testes simulados não comprovam custo ou qualidade real
do Gemini. A avaliação externa permanece na #17 e no [repasse](../HANDOFF.md).
