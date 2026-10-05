# Arquitetura: consolidar JEV sem LLM e separar documentação do MVP

Issue: [12](https://github.com/felpzw/jev-global-heatmap/issues/12).
## Objetivo e entregas

Consolidar a nova arquitetura JEV sem chamadas a LLM e integrar a documentação revisada do PR #11 à develop. Substitui #8 por mudança de escopo; não declara que a implementação foi entregue.

- [ ] Revisar/integrar ARCHITECTURE.md, docs/JEV_DESIGN.md, ADR 0002 e plano.
- [x] Separar MVP executável Gemini e snapshots anteriores em documentação histórica.
- [x] Documentar UI → JEV → fontes/datasets → normalização → estimador estatístico → reconciliação dos 195 → mapa/tabela/JSON.
- [x] Confirmar catálogo de eventos estruturados, sem interpretação universal de texto livre.
- [x] Distinguir observações, score por regras e probabilidade; vínculo com backlog novo.

Aceite: documentação integrada com links válidos, contratos/dependências coerentes e estado executável descrito corretamente. Não depende de Docker ou modelos LLM. Documento-base: docs/adr/0002-jev-without-llm.md.

## Entrega da consolidação

Branch: `docs/issue-12-architecture-consolidation`, criada de `origin/develop`.
Os commits da PR #11 foram incorporados por merge, preservando o histórico.
A revisão dos documentos está concluída nesta branch; a primeira entrega acima
só pode ser marcada integralmente após o merge à `develop`.

| Critério | Evidência documental |
| --- | --- |
| Fluxo e direção de dependências | [ARCHITECTURE.md](../../ARCHITECTURE.md) |
| Catálogo, observações, scores, probabilidades e estados | [JEV_DESIGN.md](../JEV_DESIGN.md) |
| Decisão sem LLM/Docker de modelos | [ADR 0002](../adr/0002-jev-without-llm.md) |
| Dependências e backlog #13–#17 | [Plano ativo](../JEV_IMPLEMENTATION_PLAN.md) |
| Código Gemini identificado separadamente | [MVP executável](../MVP_LEGACY.md) e [README](../../README.md) |
| Proposta anterior e ADR histórica | [Índice histórico](../legacy/README.md) |

A consolidação não implementa registro, catálogo, conectores, banco ou estimador.
O requisito `local_only` cobre aquisição/estimação; geometrias locais para a UI
são entrega futura da #16. As dependências atuais permanecem as do MVP.

## Validação em 05/10/2026

- 20 documentos Markdown e 55 links locais conferidos, sem links quebrados.
- `git diff --check` aprovado.
- `python -m unittest discover -s tests -v`: 29 testes offline aprovados.

Os testes cobrem o MVP existente. Não houve chamada real a Gemini, aquisição
externa de dados ou ensaio de previsão/calibração da JEV.
