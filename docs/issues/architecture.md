# Arquitetura: consolidar JEV sem LLM e separar documentação do MVP

Issue: [12](https://github.com/felpzw/jev-global-heatmap/issues/12).
## Objetivo e entregas

Consolidar a nova arquitetura JEV sem chamadas a LLM e integrar a documentação revisada do PR #11 à develop. Substitui #8 por mudança de escopo; não declara que a implementação foi entregue.

- [ ] Revisar/integrar ARCHITECTURE.md, docs/JEV_DESIGN.md, ADR 0002 e plano.
- [ ] Separar MVP executável Gemini e snapshots anteriores em documentação histórica.
- [ ] Documentar UI → JEV → fontes/datasets → normalização → estimador estatístico → reconciliação dos 195 → mapa/tabela/JSON.
- [ ] Confirmar catálogo de eventos estruturados, sem interpretação universal de texto livre.
- [ ] Distinguir observações, score por regras e probabilidade; vínculo com backlog novo.

Aceite: documentação integrada com links válidos, contratos/dependências coerentes e estado executável descrito corretamente. Não depende de Docker ou modelos LLM. Documento-base: docs/adr/0002-jev-without-llm.md.
