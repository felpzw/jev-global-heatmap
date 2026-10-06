# Desenho da JEV — afinidade, seleção e justificativas

Arquitetura-alvo em 05/10/2026; implementação pendente.
Regida pela [ADR 0003](adr/0003-affinity-ranking.md).

## Catálogo e interpretação

Começar com critérios de praia e idioma, sujeitos à evidência selecionada em #13.
Cada critério define id, descrição, sinônimos, tipo, unidade, operadores,
normalização para [0,1], evidências admissíveis e política de dados ausentes.
Requisitos são condições binárias; preferências recebem pesos positivos finitos.
Texto é mapeado por regras/sinônimos, sem LLM. Negação, combinações e termos
ambíguos devem ser tratados explicitamente ou devolvidos para esclarecimento.
O pedido só executa após confirmação da interpretação na UI. Consulta sem
preferências pontuáveis deve solicitar complemento antes de produzir ranking.

Exemplo: “praia e inglês oficial” pode ser confirmado como requisito
`english_official = true` e preferência de praia. Ter litoral não comprova
qualidade turística. Idioma oficial não comprova proficiência da população.
Uma preferência não é promovida silenciosamente a requisito.

## Dados e primeiro ensaio

Priorizar dataset local versionado, pequeno e reproduzível, com manifestos.
#13 compara Wikidata, fontes oficiais, Wikipedia e arquivos locais quanto a
pertinência, cobertura, licença, atualização e extração. Fonte e armazenamento
concreto são decididos nessa investigação, sem exigir servidor de banco.
Dados normalizados têm ISO alpha-3, atributo, valor/unidade, período, origem,
publicação/coleta, revisão/versão, hash e transformação. Não completar lacunas
com conhecimento do modelo. Dados insuficientes ficam explícitos, inclusive
para países que normalmente são pouco representados.

## Contratos propostos

| Estrutura | Conteúdo mínimo |
| --- | --- |
| AffinityRequest | texto original, critérios confirmados, requisitos/preferências/pesos, catalog_version, dataset_version, data_as_of, limites e modos |
| CriterionEvidence | id, ISO alpha-3, criterion_id, valor/unidade, período, origem, revisão/hash e transformação |
| CountryAffinity | ISO alpha-3, affinity_score, status, rank, fatores/contribuições, evidence_ids, selection_status, motivo e explicação |
| CandidateExplanation | ISO alpha-3, texto, evidence_ids, status/origem, provider/model/prompt_version quando houver LLM |
| AffinityResponse | schema_version, run_id, pedido, versões de registro/catálogo/dataset/ranker, política de seleção, candidate_ids, explanation_ids, countries, estado/tempos/falhas e métricas de chamadas |

Contratos separados de `HeatmapResponse`; scores qualitativos do MVP não são
importados como afinidade calculada. M49 preserva três caracteres. Tipos indevidos,
NaN/infinito, duplicatas, códigos extras e referências incompatíveis são rejeitados.
A resposta final deve igualar o conjunto do registro dos 195, não só seu tamanho.
A resposta LLM deve igualar o conjunto solicitado naquele lote; nunca os 195.

## Filtros e fórmula de score

1. Validar pedido, pesos, operadores, versões e compatibilidade dos dados.
2. Excluir país somente quando uma evidência demonstra requisito não atendido.
3. Se um requisito necessário permanece desconhecido, marcar `insufficient_data`.
4. Calcular preferências dos elegíveis com dados suficientes:
   `affinity_score = 100 * sum(weight_i * normalized_value_i) / sum(weight_i)`.
5. Ordenar pelo score não arredondado, decrescente; empate por ISO alpha-3.

A política inicial exige dados para todos os critérios ativos necessários à
pontuação. Não renormalizar apenas pelos atributos presentes nem imputar zero;
qualquer política futura precisa ser explícita, versionada e avaliada. Contribuições
individuais e denominador são exportados para reproduzir o score. Arredondamento
ocorre só na apresentação. A regra de normalização pertence ao catálogo versionado.

| Status de país | Score | Significado |
| --- | --- | --- |
| ranked | Finito em [0,100] | Elegível e pontuado; pode estar fora do top K |
| filtered_out | null | Requisito não atendido, com evidência e motivo |
| insufficient_data | null | Falta de dados impede decidir elegibilidade ou score |
| error | null | Falha técnica na avaliação do país |

Os scores não precisam somar 100. São afinidade segundo os critérios e dados do
pedido, sem interpretação probabilística ou promessa de “melhor país” universal.

## Seleção e chamada limitada à LLM

Somente países `ranked` acima do limiar configurado entram na seleção. Hipótese
inicial para avaliação: até 20 candidatos e justificativas para os 10 primeiros;
limites configuráveis, `1 <= explanation_limit <= candidate_limit <= 195`.
O limiar inicial é escolhido no protocolo #17; não é uma garantia de qualidade.
`selection_status` distingue `selected`, `not_selected` e `not_eligible`, com motivo
(limiar, limite ou status). Menos resultados são permitidos; conjunto vazio não
chama Gemini. `selected` identifica os até `candidate_limit` candidatos;
`candidate_ids` registra esse conjunto e `explanation_ids` seus primeiros
`explanation_limit` países. Apenas `explanation_ids` é enviado ao Gemini.
O ranking global dos países pontuados é preservado no JSON.

Enviar ao Gemini somente pedido confirmado, países a justificar, scores,
contribuições e evidências pertinentes. Um lote pequeno é o ponto de partida;
limites de tokens podem exigir lotes menores, sem chamada por país automática.
LLM explica os fatores recebidos e não devolve novos scores ou ranking.
Dados textuais das fontes são material de referência, não instruções ao modelo.
A resposta usa schema estrito; validar códigos, igualdade do subconjunto,
unicidade, texto e IDs de evidências pertinentes. JSON correto não prova
fundamentação factual: a avaliação inclui revisão das afirmações.

Status da explicação: `generated`, `template`, `not_requested` ou `error`.
Falha/timeout/truncamento/saída inválida mantém score e posição, registra erro e
mostra template com status `error`, origem `template` e motivo da falha.
No modo sem LLM, explicações solicitadas têm status/origem `template`. País
fora de `explanation_ids` recebe `not_requested`; seus fatores continuam disponíveis. Modelo, prompt, latência e uso/custo disponível são registrados.

## Modos, execução e cache

Separar modo de aquisição (dataset local ou conector habilitado) e explicação
(Gemini ou template). `local_only` proíbe qualquer chamada externa e força template;
ter dados locais com Gemini habilitado não é execução offline. Sem chave, ranking
continua disponível com template. Dados externos exigem configuração explícita.

`completed` admite exclusões e dados insuficientes. Erro técnico por país ou falha
da etapa LLM marca `partial`, sem invalidar os scores válidos. Pedido inválido
não inicia execução. Progresso/cancelamento/checkpoints não são resultados finais
reconciliados. Preservar resultado anterior separado pelo `run_id`.

Definir timeout/retry limitado, orçamento de tokens/chamadas, progresso e
cancelamento. Cache de ranking identifica pedido confirmado, pesos, versões,
fonte e data de referência; cache de explicação inclui também evidências,
seleção, provedor/modelo/prompt. Reruns não geram nova chamada. Retomada exige
as mesmas versões; gravação atômica e isolamento por execução/sessão.

## Heatmap e avaliação

Mapa colore todos os `ranked` em escala fixa 0–100, inclusive baixa afinidade e
países fora do top K. Destaque e tabela ordenada identificam os justificados.
Exclusão, dados insuficientes, erro e fora do registro têm estados visuais próprios.
Tabela/busca cobre os 195 e microestados; JSON preserva fatores, proveniência,
seleção e estado da explicação. O MVP fica identificado durante a migração.

#17 define antes do ensaio consultas anotadas, relevantes conhecidos, separação
entre ajuste e teste, baseline e limiares. Medir recall dos candidatos (relevantes
não descartados), precision@K e NDCG@K para o topo, requisitos violados,
ambiguidades, cobertura de dados e justificativas apoiadas nas evidências.
Comparar latência p50/p95, chamadas, tokens e custo com/sem cache e contra o
fluxo amplo no mesmo workload/provedor/modelo. Reportar diferenças de acesso a
dados entre baselines. Não afirmar economia ou qualidade sem medição.

Responsabilidades: [arquitetura](../ARCHITECTURE.md).
Dependências: [plano ativo](JEV_IMPLEMENTATION_PLAN.md).
Código disponível: [MVP](MVP_LEGACY.md). Propostas anteriores: [histórico](legacy/README.md).
