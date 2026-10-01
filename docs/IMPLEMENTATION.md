# MVP e sequência de integração

Cada branch parte da `develop` após o merge anterior. Merges usam `--no-ff`,
com objetivo, mudanças e validação na mensagem, sem trailers de coautoria.

| Ordem | Issue | Branch | Entrega |
| --- | --- | --- | --- |
| 1 | #1 | `feat/issue-1-validation-pipeline` | Contrato estrito, Gemini e smoke test |
| 2 | #2 | `feat/issue-2-map-renderer` | Figura Plotly e dados de demonstração |
| 3 | #3 | `feat/issue-3-streamlit-ui` | Interface, feedback e estado por sessão |
| 4 | #4 | `feat/issue-4-prompt-tuning` | Prompt refinado e avaliação reproduzível |

## Issue #1 — pipeline

- Implementados `CountryHeatmap`, `HeatmapResponse`, Structured Outputs e validação local.
- Adicionados `.env.example`, proteção de segredos e `test_llm.py` para execução real.
- Verificação: 9 testes offline aprovados; incluem ISO inválido, limites, duplicatas,
  JSON malformado, credenciais ausentes, timeout e erros do provedor.
- Chamada real não executada: sem credenciais, conforme opção do usuário.

## Issue #2 — mapa

- `plot_heatmap(list[dict])` retorna uma figura Plotly com projeção mundial,
  localização ISO-3, escala fixa 0–100 e justificativa no tooltip.
- Países sem dados ficam cinza; ausência não significa score zero.
- `data/demo_heatmap.json` contém oito países com scores explicitamente fictícios.
- Verificação: 3 testes do componente, cobrindo localizações, scores, tooltip,
  escala, serialização, dados vazios/inválidos e escape de HTML; 12 testes no total.

## Issue #3 — interface

- Interface Streamlit com formulário, bloqueio de input vazio, spinner, erros
  compreensíveis, mapa, tabela, download JSON e demonstração sem API.
- `session_state` mantém resposta e contexto original. Falhas preservam o último
  sucesso; uma resposta vazia substitui o resultado por uma explicação.
- Verificação: 5 testes AppTest cobrem geração, rerun sem nova chamada, demo,
  entrada vazia, falhas e resultado vazio; 17 testes offline no total.
- Conferência no Safari: formulário, demonstração, legenda e renderização do mapa.

## Issue #4 — prompt e avaliação

- Prompt refinado alinha envelope e chaves ao Pydantic, exige ISO existente,
  mantém critério comparável e proíbe contrastes artificiais e fontes inventadas.
- Baseline da etapa #1 preservado para comparação. O avaliador real alterna
  ordem por repetição e grava respostas e latência para revisão manual.
- Avaliação offline registrada em `docs/evaluations/offline.json`: quatro
  cenários passaram, incluindo scores iguais, resposta vazia e ISO inválido rejeitado.
- Verificação final: 20 testes offline aprovados; `pip check` sem dependências quebradas.
- **Pendente, conforme decisão do usuário:** smoke test com credenciais e
  comparação real baseline/refinado (precisão factual, justificativas e latência
  do provedor). Não há alegação de melhoria de qualidade ou velocidade medida.

## Escopo da entrega

MVP das quatro issues integrado à `main` pela
[PR #5](https://github.com/felpzw/jev-global-heatmap/pull/5), em 01/10/2026.
As branches de implementação foram preservadas.

## Revisão pós-merge

A revisão identificou e corrigiu dois casos no serviço:

- JSON válido era aceito mesmo quando o provedor indicava uma geração interrompida.
  Agora somente respostas concluídas com `STOP` seguem para validação Pydantic;
  limites de geração e bloqueios produzem mensagens compreensíveis e preservam o mapa anterior.
- Uma `GEMINI_API_KEY` contendo apenas espaços impedia o fallback para
  `GOOGLE_API_KEY`. As duas variáveis agora são normalizadas antes da seleção.

Foram adicionados testes com o SDK real e transporte HTTP simulado, sem rede,
além da regressão do estado da interface. A suíte passou de 20 para 27 testes.
O avaliador offline continua aprovando os quatro cenários esperados.

As correções seguem em `fix/mvp-review` → `develop`, separadas do merge original.
O encerramento das issues #1–#3 refere-se ao escopo do MVP entregue pela PR #5;
a revisão adicional precisa ser promovida da `develop` para a `main`.

### Pendências mantidas

- [ ] Executar `test_llm.py` com credenciais configuradas.
- [ ] Comparar baseline/refinado na API, registrando códigos ISO, distribuição e latência.
- [ ] Revisar a precisão factual das justificativas e documentar a conclusão da issue #4.

Essas verificações reais continuam pendentes por decisão do usuário. Testes
simulados não encerram o aceite empírico da issue #4.

Referência: [motivos de término da API Gemini](https://ai.google.dev/api/generate-content#FinishReason).
