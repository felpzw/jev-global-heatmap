# ADR 0003 — Heatmap de ranking de afinidade com JEV e justificativas LLM

- Data: 05/10/2026.
- Estado: decisão aprovada pelo responsável; implementação pendente.
- Substitui: ADR 0002 e o escopo de previsão probabilística.
- Issue: [#20](https://github.com/felpzw/jev-global-heatmap/issues/20).

## Contexto e decisão

O responsável definiu o produto como ranking de afinidade com o pedido.
A JEV interpreta critérios suportados, filtra requisitos, calcula scores 0–100
por preferências e pesos e seleciona candidatos. Gemini recebe somente os
melhores candidatos e evidências para produzir justificativas. Países sem
proximidade suficiente não consomem chamadas de explicação.

O score mede afinidade segundo dados/regras; não mede probabilidade de evento.
LLM não escolhe os países, não atribui scores e não altera a ordem. O primeiro
MVP usa catálogo pequeno, regras/sinônimos e dataset local versionado. Inputs
ambíguos ou não suportados exigem esclarecimento, sem interpretação universal.

## Consequências e alternativas

- Requisitos obrigatórios são separados de preferências graduadas.
- Falta de dados e exclusão não viram zero; baixa afinidade válida pode ser zero.
- Registro dos 195 permanece no resultado, mas justificativas LLM são limitadas.
- Templates mantêm utilidade sem chave, em local_only ou após falha da LLM.
- Embeddings, interpretação por LLM e reordenação por LLM ficam adiados até
  existir evidência de necessidade; não são dependências iniciais.
- Retorno de previsão, calibração, prazo de evento e Brier/log loss sai do backlog
  ativo. A avaliação passa a seleção, ranking, fundamentação e custo/latência.
- Limites de candidatos são hipóteses a avaliar, não promessa de economia.

A ADR 0002 e seus documentos são preservados como histórico. A #12 permanece
concluída no escopo anterior, sem ser reaberta ou declarada entrega deste produto.
As issues #13–#17 são revisadas mantendo seus números e dependências.

## Documentos ativos

[Arquitetura](../../ARCHITECTURE.md), [contratos](../JEV_DESIGN.md) e
[plano](../JEV_IMPLEMENTATION_PLAN.md). O [MVP atual](../MVP_LEGACY.md) ainda
usa Gemini para gerar os próprios scores; esta decisão não muda o executável.
[Histórico das propostas](../legacy/README.md).
