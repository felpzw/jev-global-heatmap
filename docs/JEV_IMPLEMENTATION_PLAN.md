# Plano de implementação JEV sem LLM

Atualizado em 05/10/2026. Arquitetura-alvo, sem mudança executável nesta entrega.
A nova decisão está na [ADR 0002](adr/0002-jev-without-llm.md).

## Backlog ativo

| Issue | Entrega |
| --- | --- |
| [12](https://github.com/felpzw/jev-global-heatmap/issues/12) | Arquitetura: consolidar JEV sem LLM e separar documentação do MVP |
| [13](https://github.com/felpzw/jev-global-heatmap/issues/13) | Dados: avaliar Wikipedia/Wikidata, APIs e datasets locais para a JEV |
| [14](https://github.com/felpzw/jev-global-heatmap/issues/14) | Fundação JEV: registro dos 195 Estados e contratos versionados |
| [15](https://github.com/felpzw/jev-global-heatmap/issues/15) | Motor JEV: integrar dados e estimador estatístico sem chamadas de LLM |
| [16](https://github.com/felpzw/jev-global-heatmap/issues/16) | Interface JEV: eventos estruturados, mapa, status e exportação rastreável |
| [17](https://github.com/felpzw/jev-global-heatmap/issues/17) | Avaliação JEV: baseline, qualidade probabilística e desempenho reproduzível |

## Ordem e dependências

1. #12 consolida a arquitetura e incorpora os commits documentais da PR #11
   na branch `docs/issue-12-architecture-consolidation`, destinada à `develop`.
   O aceite de integração permanece pendente até o merge dessa branch.
2. #13 investiga fontes, domínio, dataset e armazenamento. #14 implementa o
   registro dos 195 e contratos offline; podem avançar conjuntamente.
3. #15 implementa conectores/normalização, baseline/estimador e orquestração,
   após contratos e decisão de dados.
4. #16 integra formulário estruturado, status, mapa e JSON ao motor.
5. #17 define protocolo cedo e executa avaliação após dados/estimador estarem
   disponíveis. Não esperar a interface para definir baseline ou corte temporal.

## Primeira atividade

Iniciar #13 com matriz Wikipedia/Wikidata, APIs oficiais e dataset local.
Escolher domínio/evento mensurável e verificar cobertura/histórico antes de
selecionar banco ou estimador. API é meio de consulta; banco é armazenamento;
nenhum deles gera por si só uma probabilidade.

Em #14, implementar registro versionado dos 193 membros ONU + dois observadores,
M49 string com zeros preservados, validação de conjunto exato e contratos com
probabilidade/status/proveniência. Testar casos errados mesmo com 195 registros,
duplicatas/extras, referências incompatíveis, finitude/tipos/datas e round-trip.
Esses testes não precisam de rede, LLM ou Docker.

## Encerramento do backlog anterior

#4, #8 e #10 são substituídas por mudança de escopo, com motivo not_planned.
Não registrar como entregues a avaliação real de prompts, o runtime Docker ou a
integração do PR #11. A integração documental é entregue pela branch da #12 e só é concluída
após seu merge à `develop`.
Histórico preservado em [legacy](legacy/README.md) e na ADR 0001.

## Aceite transversal

- Todos os 195 representados uma vez, mesmo quando não há estimativa defensável.
- Dados observados/score/probabilidade distintos; null para insuficiência,
  inaplicabilidade e erro, com justificativa. Erro técnico indica parcial.
- Dataset, fontes/revisões, corte temporal, transformações, método e versões
  rastreáveis no resultado; nenhum valor inventado para preencher o mapa.
- Nenhuma chamada LLM; local_only também não faz consulta externa.
- Reruns/cancelamento/falhas não misturam execuções; limites e cache explícitos.
- Baseline e protocolo temporal pré-definidos; não alegar calibração sem evidência.

## Evidência desta revisão

A suíte de 29 testes offline do MVP foi aprovada em 05/10/2026. Esta mudança
altera documentação e acompanhamento; não demonstra execução da JEV, consulta
Wikipedia, banco pronto ou qualidade probabilística. O código Gemini permanece
identificado como MVP até a migração planejada.
