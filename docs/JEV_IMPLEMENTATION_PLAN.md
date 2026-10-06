# Plano de implementação — heatmap de afinidade com JEV

Atualizado em 05/10/2026. Arquitetura-alvo, sem mudança executável nesta entrega.
Decisão ativa: [ADR 0003](adr/0003-affinity-ranking.md).

## Backlog ativo

| Issue | Entrega | Dependências |
| --- | --- | --- |
| [20](https://github.com/felpzw/jev-global-heatmap/issues/20) | Consolidação documental do ranking de afinidade | Decisão do responsável |
| [13](https://github.com/felpzw/jev-global-heatmap/issues/13) | Catálogo de critérios e dataset de afinidade por país | ADR 0003; pode avançar com #14 |
| [14](https://github.com/felpzw/jev-global-heatmap/issues/14) | Registro, critérios e contratos de afinidade | ADR 0003; fixtures offline |
| [15](https://github.com/felpzw/jev-global-heatmap/issues/15) | Filtros, ranking e justificativas LLM limitadas | #13 + #14 |
| [16](https://github.com/felpzw/jev-global-heatmap/issues/16) | Heatmap, ranking, revisão do pedido e justificativas | #14 + #15 |
| [17](https://github.com/felpzw/jev-global-heatmap/issues/17) | Seleção, ranking, fundamentação e custo/latência | Protocolo cedo; ensaio após #13 + #15 |

Os requisitos locais espelham as issues: [dados](issues/data.md),
[fundação](issues/foundation.md), [motor](issues/engine.md),
[interface](issues/ui.md) e [avaliação](issues/evaluation.md).
A [consolidação](issues/affinity-architecture.md) acompanha a #20.

## Ordem e primeiro MVP

1. Integrar a decisão/documentação #20 à develop, preservando o histórico.
2. Iniciar #13 com praia e idioma: definir atributos realmente mensuráveis,
   fontes licenciadas e dataset local versionado, sem selecionar banco servidor.
   Em paralelo, #14 implementa registro e contratos com fixtures identificadas.
3. #17 define consultas anotadas, baseline e limiares antes de ajustar regras.
4. #15 implementa parser por regras/sinônimos, filtros e score determinístico,
   seleção limitada e Gemini para justificativas apoiadas nas evidências.
5. #16 integra revisão de critérios, heatmap, ranking, tabela e JSON ao motor.
6. #17 executa e publica avaliação reproduzível, com custo e latência reais quando
   autorizado o ensaio. Fixtures não comprovam economia ou fundamentação real.

Hipótese inicial: até 20 candidatos e 10 justificativas, com limiar a definir
no protocolo. Não exige preencher os limites quando houver poucos relevantes.
Score por média ponderada dos critérios normalizados, sem reordenação LLM.
Catálogo/parser inicial não interpreta qualquer tema; entradas desconhecidas ou
ambíguas exigem esclarecimento. Ranking funciona sem chave com templates.

## Aceite transversal

- Requisitos e preferências separados, interpretação visível e confirmada.
- Exatamente 195 registros finais; score 0–100 para ranked, null para exclusão,
  dados insuficientes ou erro. Nenhuma conversão de score em probabilidade.
- Fatores, pesos, normalização, dados/fontes e versões reproduzem o resultado.
- LLM recebe apenas selecionados; códigos/evidências validados, score/ordem imutáveis.
- Dados ausentes não recebem zero; top K vazio não chama Gemini.
- local_only não usa rede e força templates; geometrias locais são necessárias
  para oferecer UI integralmente offline, pois o MVP usa CDN.
- Falha de justificativa preserva ranking e registra fallback; reruns, cache e
  retomada respeitam identidade da execução e versões.
- Avaliação cobre falsos descartes, precision/recall/NDCG, requisitos,
  fundamentação e tokens/custo/latência, com limiares definidos antes do ensaio.

## Histórico e estado executável

#12 foi concluída pela integração das PRs #11 e #18 à develop; seu escopo era
consolidar previsão sem LLM. Ela permanece encerrada. ADR 0002 e documentos são
[snapshots históricos](legacy/README.md), sem apagar a decisão anterior.
#4, #8 e #10 continuam substituídas por mudança de escopo; não reabrir tuning,
previsão ou Docker. As #13–#17 mantêm números e recebem requisitos revisados.

O código atual é o [MVP Gemini](MVP_LEGACY.md), no qual o modelo gera os scores.
Esta revisão não implementa parser, dataset ou ranking da JEV nem demonstra
economia, qualidade de busca ou fundamentação das justificativas.
