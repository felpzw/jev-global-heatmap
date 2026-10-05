# Fundação JEV: registro dos 195 Estados e contratos versionados

Issue: [14](https://github.com/felpzw/jev-global-heatmap/issues/14).
## Objetivo e entregas

Implementar fundação offline sem SDK/LLM/Docker/UI.

- [ ] Registro versionado 193 membros ONU + Santa Sé/VAT e Palestina/PSE, ISO alpha-3/M49, fontes e data de consulta.
- [ ] country_registry.py e forecast_schema.py: pedido estruturado, observação/evidência, previsão por país e execução.
- [ ] Domínio/evento, indicador/unidade/limiar, prazo, resolução e as_of; ambiguidade não inicia execução.
- [ ] Separar dados observados, score de regras e probabilidade; estimated em [0,1], insufficient_evidence/not_applicable/error com null.
- [ ] Metadados de dataset/transformação/estimador e versões, sem campos LLM obrigatórios.
- [ ] Validar conjunto exato dos 195 no resultado final, unicidade, finitude/tipos/datas e referências de dados pertinentes.
- [ ] Fixtures fictícias e testes de conjunto errado com 195 itens, faltas/extras, duplicatas, NaN e evidências inválidas.

Aceite: suíte offline e round-trip JSON aprovados. Sem conversão de heat_score em probabilidade. Cobertura de registros não exige cobertura de estimativas. Depende da decisão arquitetural; não exige seleção do banco nem consulta externa.
