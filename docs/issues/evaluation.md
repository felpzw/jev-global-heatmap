# Avaliação JEV: seleção, ranking, justificativas e custo

Issue: [17](https://github.com/felpzw/jev-global-heatmap/issues/17).

## Objetivo e dependências

Avaliar afinidade e redução do contexto enviado à LLM, conforme ADR 0003.
Definir protocolo desde o início; ensaio depende dos dados #13 e motor #15.
Substitui métricas de previsão probabilística, sem declarar ensaios anteriores feitos.

## Entregas

- [ ] Consultas anotadas e critérios de relevância: praia, idioma, combinações, negações, ambiguidades, nenhum resultado e dados ausentes; revisão humana dos relevantes conhecidos.
- [ ] Separar ajuste/teste e definir baselines, K, limiar de seleção, pesos e metas antes do ensaio; testar hipótese de 20 candidatos/10 justificativas.
- [ ] Recall dos candidatos, precision@K e NDCG@K, requisitos violados, cobertura por país/critério e falsos descartes; métricas agregadas e por tipo de consulta.
- [ ] Comparar ranking simples por regras e fluxo amplo Gemini, com mesmo workload/provedor/modelo; registrar diferenças de evidências acessíveis aos baselines.
- [ ] Revisar fundamentação das justificativas e referências, fatos não suportados, consistência com fatores/scores e preservação da ordem; schema válido não comprova veracidade.
- [ ] Medir chamadas, tokens, custo quando disponível e latência p50/p95, com/sem cache, incluindo aquisição e explicação; verificar que países não selecionados não consomem explicação LLM.
- [ ] Testar ranking sem chave, local_only, falha/truncamento/retorno inválido LLM e retomada; relatório de limitações do dataset e agregação nacional.
- [ ] Publicar scripts, versões, consultas, rótulos, ambiente e relatório reproduzível; fixtures não substituem medição real de custo/qualidade.

## Aceite

Relatório contra baselines e metas pré-definidas, com limites e lacunas. Não
alegar economia, precisão universal ou qualidade de ranking sem evidência.
Brier/log loss/calibração de probabilidades deixam este escopo.
