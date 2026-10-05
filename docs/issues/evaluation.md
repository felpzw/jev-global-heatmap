# Avaliação JEV: baseline, qualidade probabilística e desempenho reproduzível

Issue: [17](https://github.com/felpzw/jev-global-heatmap/issues/17).
## Objetivo e entregas

Validar previsões e operação sem confundir cobertura/JSON/scores com qualidade preditiva. Novo escopo de avaliação substitui tuning #4, sem declarar ensaios antigos realizados.

- [ ] Definir domínio/evento, baseline, desfechos observáveis, amostra e protocolo/limiares antes do teste.
- [ ] Separação temporal desenvolvimento/calibração/teste, snapshots disponíveis em as_of e previsões prospectivas arquivadas.
- [ ] Brier/log loss/curvas de confiabilidade com política para extremos, cobertura/abstenção/erros e incerteza das métricas.
- [ ] Considerar dependência entre países/eventos, sem presumir 195 observações independentes.
- [ ] Revisar fontes/normalização; benchmark p50/p95, recursos, consultas e custo aplicável, com/sem cache no mesmo workload.
- [ ] Publicar scripts, ambiente, versões de dataset/estimador e relatório reproduzível.

Aceite: relatório contra baseline com limitações e limiares pré-definidos. Manter não calibrado até evidência fora da amostra. Fixtures não substituem ensaio real. Depende de dados/domínio e estimador definidos.
