# Interface JEV: eventos estruturados, mapa, status e exportação rastreável

Issue: [16](https://github.com/felpzw/jev-global-heatmap/issues/16).
## Objetivo e entregas

Disponibilizar JEV sem LLM no Streamlit, identificada separadamente do MVP qualitativo durante a migração.

Dependências: contratos e motor JEV.

- [ ] Catálogo de domínios/eventos suportados, indicador/unidade/limiar/prazo e resolução explícitos.
- [ ] Contexto livre opcional não seleciona silenciosamente evento/método. Fonte/dataset e local_only/consulta externa selecionáveis.
- [ ] Progresso/cancelamento/parcial e preservação do resultado anterior com sua identidade.
- [ ] Probabilidade (%) apenas estimated; nulos/status explícitos e fora do escopo distinto.
- [ ] Tabela/busca para os 195 e microestados; revisão de geometria sem atribuir valores a vizinhos.
- [ ] JSON com pedido/as_of, fontes/revisões, dataset, método/parâmetros, versões e falhas.
- [ ] Reruns não repetem consultas; testes de sessão e regressões do MVP.

Aceite: fluxo integrado com dados fictícios identificados e sem chave LLM. Nenhuma aba de modelos necessária. Offline integral exige geometrias locais; registrar a limitação do CDN atual.
