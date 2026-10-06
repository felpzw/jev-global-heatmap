# Dados: catálogo de critérios e dataset de afinidade por país

Issue: [13](https://github.com/felpzw/jev-global-heatmap/issues/13).

## Objetivo

Selecionar critérios mensuráveis e evidências para ranking de afinidade com o
pedido, conforme ADR 0003. Revisão do escopo anterior de previsão sem LLM;
não declara concluída a investigação anterior. Pode avançar com #14.

## Entregas

- [ ] Catálogo inicial pequeno para praia e idioma: definições, sinônimos, tipos, unidades, operadores e ambiguidades; distinguir litoral/praia turística e inglês oficial/proficiência.
- [ ] Fontes pertinentes e licenciadas: comparar Wikidata, Wikipedia, fontes oficiais e datasets locais por cobertura dos 195, qualidade, atualização e reprodução.
- [ ] Dataset local versionado com manifestos e amostra reproduzível; aquisição sem LLM, sem obrigar banco servidor ou consulta online durante ranking.
- [ ] Normalização por ISO alpha-3, atributo, valor/unidade e período; ausência de dados explícita, sem completar com conhecimento da LLM.
- [ ] Proveniência por evidência: URL/arquivo, publicação/coleta, revisão/versão, hash e transformação; relatório de cobertura por critério/país.
- [ ] Definir normalização para [0,1], requisitos e preferências, política de missing data, atualizações, retenção e limites de aquisição.
- [ ] Registrar seleção em ADR de dados; justificar armazenamento e eventuais conectores externos, sem downloads indiscriminados.

## Aceite

Catálogo, dataset/amostra e matriz de fontes reproduzíveis, com licença,
proveniência e lacunas. Não exige dados válidos para todos os países, previsão
ou LLM. Dados de país não garantem condições de cada cidade/região. Integração
com #15 depende dos contratos de #14.
