# Motor JEV: filtros, ranking e justificativas LLM limitadas

Issue: [15](https://github.com/felpzw/jev-global-heatmap/issues/15).

## Objetivo e dependências

Implementar pedido → critérios → dados → filtros → ranking → seleção →
justificativas, conforme ADR 0003. Depende de #13 e #14. Primeiro ensaio com
regras/sinônimos e dataset local; sem previsão, embeddings ou runtime Docker.

## Entregas

- [x] Parser por catálogo/sinônimos; tratar negações e combinações suportadas, exigir esclarecimento de ambiguidades/termos desconhecidos e confirmar critérios antes da execução.
- [x] Leitura/normalização de dataset com proveniência; requisito só exclui com evidência de descumprimento, desconhecido gera insufficient_data.
- [x] Score 100 * soma(peso * valor normalizado) / soma(pesos), com contribuições e política inicial de dados completos para critérios ativos; sem imputar zero ou renormalizar atributos ausentes.
- [x] Ranking estável por score não arredondado e desempate ISO; resposta final representa os 195 uma vez.
- [x] Seleção por limiar e top K configuráveis; hipótese de até 20 candidatos/10 justificativas a avaliar em #17, sem completar artificialmente e sem LLM para conjunto vazio.
- [x] Adaptador Gemini envia apenas selecionados, pedido confirmado e evidências; resposta estruturada não pode adicionar países, scores ou reordenar.
- [x] Validar lote exato, códigos, duplicatas e IDs pertinentes; texto de fonte tratado como dados, não instruções; testes de retorno indevido e geração interrompida.
- [x] Templates sem chave, em local_only ou após falha da LLM; preservar scores/ordem, registrar origem/erro e execução parcial quando houver falha técnica.
- [x] Limites de tokens/chamadas/retries, timeout, progresso/cancelamento, métricas e cache de ranking/explicação por pedido, dados, regras, seleção e modelo/prompt; isolamento de sessão e checkpoints atômicos.
- [x] Testes comprovam ausência de chamadas ao parser/ranker e países não selecionados; local_only não usa rede; reruns e retomada não misturam versões.

## Aceite

Execução reproduzível em dataset local com 195 estados, fatores e evidências.
LLM simulada prova envio restrito e preservação dos scores após falha. Ranking
funciona sem credenciais; integração real com Gemini é identificada separadamente.
Sem alegação de economia ou qualidade antes do ensaio #17.

## Evidências de implementação em 18/10/2026

Consulte [DELIVERY.md](../DELIVERY.md), [fontes e reprodução](../../data/SOURCES.md)
e a suíte offline. Integração destinada à `develop`; a PR registra o estado remoto.
O snapshot é histórico; testes simulados não comprovam custo ou qualidade real
do Gemini. A avaliação externa permanece na #17 e no [repasse](../HANDOFF.md).
