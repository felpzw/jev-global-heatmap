# Desenho da JEV — afinidade, seleção e justificativas

Desenho de 05/10/2026; catálogo inicial implementado em 18/10/2026.
Detalhes de execução, evidências e limites: [entrega](DELIVERY.md), [fontes](../data/SOURCES.md) e [repasse](HANDOFF.md).
Regida pela [ADR 0003](adr/0003-affinity-ranking.md).

## Catálogo e interpretação

O catálogo implementado cobre litoral marítimo e inglês oficial nacional.
Cada critério define id, descrição, sinônimos, tipo, unidade, operadores,
normalização para [0,1], evidências admissíveis e política de dados ausentes.
Requisitos são condições binárias; preferências recebem pesos positivos finitos.
Texto é mapeado por regras/sinônimos, sem LLM. Negação, combinações e termos
ambíguos devem ser tratados explicitamente ou devolvidos para esclarecimento.
O pedido só executa após confirmação da interpretação na UI. Consulta sem
preferências pontuáveis deve solicitar complemento antes de produzir ranking.

Exemplo: “praia e inglês oficial” exige esclarecer praia antes de confirmar
uma preferência de litoral. O usuário pode escolher inglês como requisito
e litoral como preferência. Ter litoral não comprova qualidade turística. Idioma oficial não comprova proficiência da população.
Uma preferência não é promovida silenciosamente a requisito.

## Dados e primeiro ensaio

O dataset local usa JSON/JSONL e manifesto. A pesquisa da #13 comparou fontes
e armazenamento; a release usa extratos históricos do Factbook, com litoral
para 195 Estados e idioma para 133. Veja [SOURCES.md](../data/SOURCES.md).
Dados normalizados têm ISO alpha-3, atributo, valor/unidade, período, origem,
publicação/coleta, revisão/versão, hash e transformação. Não completar lacunas
com conhecimento do modelo. Dados insuficientes ficam explícitos, inclusive
para países que normalmente são pouco representados.

## Contratos implementados

| Estrutura | Conteúdo mínimo |
| --- | --- |
| AffinityRequest | text, criteria (attribute_id, expected, role, weight), confirmed, local_only, threshold, candidate_limit, explanation_limit |
| CriterionEvidence | evidence_id, ISO alpha-3, attribute_id, value, data_status, reason, source_url/file/sha256/revision, collected_at, published_at, reference_period, license e transformation |
| CountryAffinity | ISO alpha-3, name, affinity_score, status, rank, reason, factors (critério/evidência/normalizado/contribuição), selection, explanation_status/source e explanation |
| CandidateExplanation | iso_alpha_3, text, evidence_ids; status/origem ficam em CountryAffinity e provedor/modelo/prompt em metadata |
| AffinityResponse | run_id, status, request, countries, candidate_ids, explanation_ids e metadata (versões, identidade, provider/model/prompt_version, metrics e errors) |

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
individuais e pesos são exportados; o denominador é a soma dos pesos das preferências. Arredondamento
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
limites configuráveis, `0 <= explanation_limit <= 10`, `1 <= candidate_limit <= 20`
e `explanation_limit <= candidate_limit`.
O limiar inicial é escolhido no protocolo #17; não é uma garantia de qualidade.
`selection` distingue `selected`, `not_selected` e `not_eligible`, com motivo
(limiar, limite ou status). Menos resultados são permitidos; conjunto vazio não
chama Gemini. `selected` identifica os até `candidate_limit` candidatos;
`candidate_ids` registra esse conjunto e `explanation_ids` seus primeiros
`explanation_limit` países. Apenas `explanation_ids` é enviado ao Gemini.
O ranking global dos países pontuados é preservado no JSON.

Enviar ao Gemini somente pedido confirmado, países a justificar, scores,
contribuições e evidências pertinentes. Um lote pequeno é o ponto de partida;
limites de tokens podem exigir lotes menores, sem chamada por país automática.
LLM explica os fatores recebidos e não devolve novos scores ou ranking.
Textos brutos das fontes e texto livre do pedido não são enviados. O payload contém
critérios confirmados, valores tipados, IDs internos e scores; tudo é tratado como dado.
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

Orçamento: uma chamada, 30 s, 4096 tokens de saída, sem retries adicionais.
Cancelamento cooperativo é verificado por país e antes/depois da chamada; não
interrompe uma solicitação já enviada. Um cache composto de execução por sessão
identifica pedido, pesos, hash do dataset, versões, seleção, modelo e prompt. Reruns não geram nova chamada. Retomada exige
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
Ponto de entrada: `src/app.py`. Código legado: [MVP](MVP_LEGACY.md). Propostas anteriores: [histórico](legacy/README.md).
