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
