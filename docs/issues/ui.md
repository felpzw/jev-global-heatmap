# Interface JEV: heatmap de afinidade, ranking e justificativas

Issue: [16](https://github.com/felpzw/jev-global-heatmap/issues/16).

## Objetivo e dependências

Integrar ranking de afinidade ao Streamlit, separado do MVP Gemini durante
migração. Depende de #14 e #15; conforme ADR 0003.

## Entregas

- [ ] Pedido textual com interpretação visível: confirmar requisitos/preferências/pesos, corrigir ambiguidades e informar critérios não suportados antes de executar.
- [ ] Seleção de dataset/modo e limites; comunicar que dados locais + Gemini ainda usam rede, enquanto local_only força templates.
- [ ] Heatmap de affinity_score 0–100 para todos os ranked; não exibir porcentagem/probabilidade; scores de pedidos distintos não são diretamente comparáveis.
- [ ] Distinguir baixa afinidade/zero válido, exclusão, dados insuficientes, erro e fora do registro; destacar selecionados e origem da justificativa.
- [ ] Ranking, fatores, pesos e evidências; tabela/busca para os 195 e microestados sem inventar geometrias/atribuir valores a vizinhos.
- [ ] Progresso, cancelamento, parcial e fallback após falha da LLM; resultado anterior preservado com identidade própria, sem repetir consultas em reruns.
- [ ] JSON versionado com pedido confirmado, dados, catálogo, ranker, seleção, contribuições, justificativas/modelo/prompt e métricas/falhas.
- [ ] Demonstração fictícia identificada, fluxo sem chave e regressões de sessão/MVP; documentar CDN atual e fornecer geometrias locais se oferecer UI integralmente offline.

## Aceite

Fluxo completo em fixtures identificadas, revisão dos critérios, mapa/tabela/JSON
coerentes e testes de sessão. País fora do top K pode ter score e fatores, sem
justificativa LLM. Ausência/falha de credenciais não impede o ranking.
