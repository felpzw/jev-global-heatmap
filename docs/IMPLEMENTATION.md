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
