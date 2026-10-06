# Fundação JEV: registro, critérios e contratos de afinidade

Issue: [14](https://github.com/felpzw/jev-global-heatmap/issues/14).

## Objetivo

Implementar fundação offline do ranking, sem SDK LLM, Streamlit ou Docker.
Escopo revisado pela ADR 0003; substitui contratos de previsão probabilística.
Pode avançar junto com #13 usando fixtures fictícias identificadas.

## Entregas

- [ ] Registro versionado dos 193 membros ONU + Santa Sé/VAT e Palestina/PSE; ISO alpha-3, M49 string de três caracteres, fontes e data.
- [ ] country_registry e affinity_schema: AffinityRequest, CriterionEvidence, CountryAffinity, CandidateExplanation e AffinityResponse.
- [ ] Catálogo versionado, critérios confirmados, requisitos/preferências/pesos positivos finitos e políticas de normalização/dados ausentes.
- [ ] Score finito em [0,100] apenas para ranked; filtered_out/insufficient_data/error com null, motivo e evidências pertinentes.
- [ ] Separar seleção (selected/not_selected/not_eligible) e explicação (generated/template/not_requested/error) do status e score do país.
- [ ] Metadados de dataset/catalog/ranker e execução; modelo/provedor/prompt somente quando houver LLM; falha da explicação não altera score.
- [ ] Validar exatamente o registro dos 195 no resultado final e o subconjunto solicitado em cada lote LLM; limites de seleção coerentes, candidate_ids e explanation_ids (subconjunto ordenado dos candidatos).
- [ ] Testes de faltas/extras mesmo com 195 itens, duplicatas, NaN/infinito, pesos/tipos/IDs inválidos, estados incompatíveis e round-trip JSON.

## Aceite

Suíte offline e round-trip aprovados, contratos desacoplados de LLM/UI e
HeatmapResponse. Não converter heat_score legado em afinidade calculada nem
score em probabilidade. Dados concretos serão escolhidos em #13.
