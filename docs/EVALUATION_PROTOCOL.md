# Protocolo de avaliação de afinidade — v1

Definido em 18/10/2026 antes da execução de `evaluate_affinity.py`.

O ensaio offline verifica a implementação em fixtures sintéticas, com rótulos
explícitos independentes da execução. Não mede relevância percebida por usuários,
veracidade das fontes, ganho sobre busca semântica universal ou economia monetária.

- Dataset: `synthetic-demo-v1`, oito países com valores definidos; demais posições
  permanecem ausentes. Registro de 195; catálogo `coast-language-v1`.
- Separação: um caso `tune` documenta configuração; seis casos `test` ficam fixos.
  Dois pedidos adicionais verificam esclarecimento, sem execução automática.
- K de relatório: 3; seleção: limiar 50, até 20 candidatos/10 justificativas.
  Caso vazio usa limiar 1 e pesos/atributos descritos no arquivo de casos.
- Relevância: grau 3 para combinação completa, 1 para compatibilidade parcial
  explicitamente relevante, 0 para não relevante. Rótulo ausente não é fato negativo
  sobre um país; neste ensaio sintético significa fora do conjunto relevante anotado.
- Métricas: recall dos candidatos, precision@3 (denominador 3 mesmo com menos
  resultados), NDCG@3 com ganho `2**grau-1`, falsos descartes e requisitos violados.
  Conjunto relevante vazio: recall/NDCG nulos, seleção deve ser vazia.
- Metas funcionais: zero requisito violado; zero falso descarte dos relevantes
  anotados nestas fixtures; zero chamadas no modo local; esclarecimento de todos
  os casos ambíguos; paridade de ordenação com baseline simples de contagem de
  correspondências nos casos anotados. Paridade não demonstra superioridade.
- Baseline offline: regra independente, sem pesos, sobre os mesmos booleanos,
  requisitos e política de dados completos. Publicar diferenças quando houver.
- Latência: cinco repetições por consulta, ranking sem cache e recuperação do
  cache de sessão; percentis por interpolação linear. Aquisição é etapa separada,
  não medida pelo tempo de ranking. Ambiente e versões constam no relatório.

`--live --repeats 3` adiciona comparação alternada entre JEV com explicações
restritas e Gemini amplo usando o mesmo modelo, critérios e evidências sintéticas.
O baseline amplo recebe os 195 registros (inclusive lacunas), calcula seleção e
justificativas; JEV envia somente os selecionados e já calcula os scores localmente.
O limite de saída é 4096 tokens e o timeout é 30 s, uma tentativa por chamada.
Truncamento do baseline deve ser registrado como falha, sem medir como economia.

Esse ensaio é diferente de comparar os scores livres do MVP em temas arbitrários.
O acesso às evidências é igual, mas a tarefa solicitada ao modelo é diferente:
esse é justamente o contraste arquitetural; não isola só o efeito de tamanho do
prompt. As chamadas reais retornam tokens quando disponíveis, latência e texto
para revisão. Custo permanece null sem uma tarifa verificada; preços não são
inferidos de tokens. A execução pode gerar cobrança no provedor.

A revisão humana deve marcar cada afirmação como sustentada, não sustentada ou
inconclusiva, conferir evidence_ids, ordem e requisitos e registrar revisor/data.
Rótulos sintéticos não substituem julgamento de consultas reais. Antes de alegar
qualidade externa, revisar vigência do snapshot e anotar um conjunto independente
de pedidos reais, sem ajustar o parser sobre o teste.

Resultados reais de custo e revisão humana permanecem pendentes quando não há
credenciais/revisor. O relatório publica esses campos como não executados.
