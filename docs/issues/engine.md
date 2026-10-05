# Motor JEV: integrar dados e estimador estatístico sem chamadas de LLM

Issue: [15](https://github.com/felpzw/jev-global-heatmap/issues/15).
## Objetivo e entregas

JEV como serviço de aplicação que coordena coleta/importação, normalização, estimativa e reconciliação dos 195.

Dependências: fundação + decisão sobre dados/domínio. Não depende de #10 ou SDK Gemini.

- [ ] Serviço de dados/evidências com interface para dataset local e conectores explicitamente habilitados.
- [ ] Estimador intercambiável com baseline e método apropriado ao evento/histórico; registrar versão/parâmetros/pré-requisitos.
- [ ] Planejamento determinístico, corte temporal, exatamente um resultado por Estado; sem probabilidade inventada.
- [ ] Limites de consultas, timeout/retry, concorrência/lotes quando necessários, progresso/cancelamento, cache/checkpoints isolados por execução/sessão e retenção.
- [ ] Explicações por templates com valores, método e fontes.
- [ ] Execução parcial para erros; retomada não mistura pedidos/snapshots/versões.
- [ ] Testes comprovam ausência de chamadas Gemini/LLM; local_only também não usa rede.

Aceite: execução reproduzível em dataset local com proveniência e 195 registros; estados/falhas corretos. Regras de score não preenchem probabilidade sem método válido. Nenhuma alegação de calibração ou redução de custo sem ensaio.
