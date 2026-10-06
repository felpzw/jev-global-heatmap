# Arquitetura: direcionar heatmap para ranking de afinidade com JEV

Issue: [20](https://github.com/felpzw/jev-global-heatmap/issues/20).

## Objetivo

Consolidar o projeto como heatmap de ranking de afinidade com o pedido. A JEV
interpreta critérios suportados, filtra e calcula scores 0–100; Gemini justifica
somente os melhores selecionados usando evidências, sem alterar scores ou ordem.

## Entregas

- [ ] Registrar ADR 0003 e preservar ADR 0002/documentos anteriores como histórico.
- [ ] Atualizar README, arquitetura e desenho: catálogo, requisitos/preferências, dados locais, ranking, seleção, explicação e fallback.
- [ ] Definir contratos de afinidade, estados, proveniência, limites e modo local_only sem rede.
- [ ] Reorganizar #13–#17 e plano, substituindo previsão probabilística por afinidade e avaliação de ranking/custo.
- [ ] Validar links e consistência documental e integrar a nova branch à develop.

## Aceite

Documentação e issues coerentes com ADR 0003, integradas à develop. Implementação
permanece nas #13–#17; o executável atual ainda é o MVP Gemini que gera seus
próprios scores. #12 permanece concluída no escopo anterior.
