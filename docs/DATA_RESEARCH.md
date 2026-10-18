# Issue #13 — pesquisa de armazenamento, aquisição e manutenção

> Pesquisa histórica de 05/10/2026, preservada antes da implementação. A decisão
> executada e o snapshot publicado em 18/10 estão em [SOURCES.md](../data/SOURCES.md),
> [ADR 0004](adr/0004-local-affinity-data.md) e [DELIVERY.md](DELIVERY.md).
> As descrições de pendências abaixo registram o estado da pesquisa original.

Data da análise: 05/10/2026. Estado: investigação inicial, com recomendação
provisória. Escopo: [#13](https://github.com/felpzw/jev-global-heatmap/issues/13),
conforme [ADR 0003](adr/0003-affinity-ranking.md).

## Recomendação inicial

Começar com um **snapshot local em JSON/JSONL, versionado no Git**, com catálogo,
evidências e manifesto separados. Carregar os dados validados em um índice Python
por `(iso_alpha3, attribute_id)` para o ranking. Aquisição e atualização ocorrem
em uma etapa própria, antes de publicar o snapshot; o ranking lê uma versão fixa.

Usar **Wikidata como candidato à aquisição estruturada de idiomas oficiais** e
fontes oficiais para revisar definições, negativas e conflitos. Para litoral,
avaliar Natural Earth e curadoria documentada. Proficiência em inglês e qualidade
de praia continuam em investigação: os candidatos examinados não sustentam ainda
um critério comparável, licenciado e validado para esse uso.

Esta é uma escolha de engenharia para um catálogo pequeno, não resultado de
benchmark. Dois atributos em 195 Estados representam 390 posições de cobertura;
múltiplas fontes e períodos podem produzir mais evidências. SQLite é a alternativa
seguinte se a consulta a históricos justificar SQL. Parquet/DuckDB ficam para
dados analíticos maiores. A proposta está na [ADR 0004](adr/0004-local-affinity-data.md).

## Situação encontrada no projeto

- `data/demo_heatmap.json` contém scores fictícios do MVP Gemini; não é fonte de
  atributos e não deve alimentar o ranking de afinidade.
- O dataset de afinidade, o registro dos 195 e os contratos novos ainda não
  existem. A interface dos dados precisa ser alinhada à #14.
- A política ativa exige dados para todos os critérios necessários do pedido.
  Ausência não recebe zero, nem provoca renormalização dos pesos presentes.
- Nesta etapa foram consultadas documentações de fornecedores e descrições de
  dados. Não foi adquirido um dataset nem medida a cobertura real dos 195.

## Comparação das estruturas locais

As avaliações de adequação abaixo são inferências para o workload do projeto.

| Alternativa | Benefícios para a JEV | Custo/limitação | Indicação inicial |
| --- | --- | --- | --- |
| JSON/JSONL + manifesto | Diff legível, revisão por evidência, valores tipados, proveniência aninhada e leitura com biblioteca padrão | Relações, unicidade e consistência dependem de validação; JSON não tem transações entre arquivos | Base canônica inicial; snapshot imutável publicado por inteiro |
| CSV + manifesto | Fácil inspeção tabular e intercâmbio | Nulos, booleanos, listas e referências exigem convenções extras; M49 pode perder zeros em ferramentas | Exportação, não formato canônico |
| SQLite | SQL, índices, relações e transações em arquivo local; Python oferece `sqlite3` | Banco binário dificulta diff no Git; exige esquema, migração e política de escrita | Alternativa para histórico/consultas; inicialmente só como derivação reconstruível, se necessária |
| Parquet + DuckDB | Parquet é colunar e comprimido; DuckDB atende consultas analíticas sem servidor | Binários e ferramentas adicionais; pouco benefício demonstrado no catálogo pequeno | Reavaliar com séries temporais ou volume analítico medido |
| PostgreSQL/serviço remoto | Pode atender uma futura operação com vários escritores e acesso centralizado | Operação de serviço e dependência de infraestrutura além do problema atual | Adiado; não é necessário ao primeiro dataset local |

SQLite documenta usos locais e limites de concorrência em
[Appropriate Uses](https://www.sqlite.org/whentouse.html); a integração Python está
em [sqlite3](https://docs.python.org/3/library/sqlite3.html). Caso seja adotado,
ativar e verificar `PRAGMA foreign_keys = ON`, conforme
[Foreign Key Support](https://www.sqlite.org/foreignkeys.html).
A distinção entre formato e motor está nas documentações de
[Parquet](https://parquet.apache.org/docs/overview/) e
[DuckDB](https://www.duckdb.org/why_duckdb).

Reabrir a escolha quando houver necessidade concreta de consultar muitas versões,
escritas concorrentes ou dificuldade medida de carregar o snapshot. Comparar
tamanho, tempo de carga, memória, consulta e reconstrução no mesmo conjunto.
O número de países sozinho não determina o formato.

## Atributos candidatos e semântica

Esta tabela é um esboço para o catálogo da #14, não habilitação de critérios.

| Atributo | Definição proposta | Tipo/unidade e operador | Normalização candidata | Ambiguidade/limitação |
| --- | --- | --- | --- | --- |
| `has_maritime_coast` | Há litoral oceânico ou de mar conectado ao oceano no território coberto pela política geográfica do catálogo | Booleano, sem unidade; `eq` | true → 1; false comprovado → 0 | “Litoral”, “costa marítima”; não prova praia, acesso público ou qualidade. Definir tratamento de territórios ultramarinos; excluir lagos/Cáspio |
| `english_official` | Inglês tem status oficial nacional vigente, de acordo com evidência admissível | Booleano, sem unidade; `eq` | true → 1; false comprovado → 0 | “Inglês oficial”, “idioma oficial inglês”; separar status regional, uso de facto e idioma de trabalho |
| `english_proficiency` | Medida de proficiência de uma população definida por pesquisa comparável | Numérico; escala, período e operadores ainda por selecionar | Pendente de escala e estudo; não aplicar min-max do lote automaticamente | “Facilidade de comunicação”, “fala inglês”; não inferir a partir de idioma oficial |
| `beach_suitability` | Adequação de praias a uma finalidade e, se necessário, época definidas | Pendente | Pendente | “Praia”, “boa praia”; exige localização, finalidade e dados pertinentes, não só litoral |

Booleanos também podem compor preferências se isso for confirmado no pedido;
um requisito não contribui automaticamente para score. Um pedido apenas com
requisitos precisa de preferência pontuável, conforme o desenho atual.
“Praia e inglês” exige esclarecimento antes de virar critérios suportados.

## Matriz de fontes candidatas

Cobertura abaixo é potencial/limitação documentada, não contagem de dados válidos
no registro do projeto. Cada fonte deve ser conciliada com os 195 Estados da #14.

| Fonte | Utilidade e qualidade | Cobertura/lacunas | Licença/reuso | Aquisição e manutenção sugeridas |
| --- | --- | --- | --- | --- |
| Wikidata | `P37` representa idioma oficial; estrutura permite rastrear declarações e referências. É agregador, sujeito a inconsistências | Medir países com declaração vigente, escopo nacional e evidência admissível; falta de inglês em P37 não comprova false | Dados estruturados CC0; licença não se estende automaticamente ao texto das fontes referenciadas | Descoberta restrita por SPARQL; preservar JSON de entidades com revisão fixa; revisão mensal de alterações relevantes |
| Wikipedia | Útil para descobrir referências e conferir contexto; tabelas/texto são mais frágeis para extração uniforme | Artigos, idiomas, definições e referências variam; não há cobertura validada | Texto geralmente CC BY-SA 4.0, com exceções e atribuição; verificar conteúdo reutilizado | Consulta editorial e revisão fixa quando usada; não usar scraping de páginas como fonte automática principal |
| Fontes oficiais nacionais | Candidatas preferenciais para status legal e escopo; permitem revisão de conflitos | Fragmentadas por país, idioma, formato e vigência; comparabilidade depende do atributo | Verificar termos de cada publicação/arquivo; acesso público não define licença | Curadoria pequena com URL, seção, vigência, coleta e evidência; revisão por mudança ou calendário |
| Natural Earth | Geometrias candidatas para derivar litoral; não mede turismo nem qualidade de praia | Reconciliar unidades cartográficas, microestados e soberania; costa inclui Cáspio e tem limitações de resolução | Domínio público | Fixar release e arquivos específicos de costa e países; derivação geográfica versionada e revisão de casos-limite |
| GeoNames `countryInfo.txt` | Arquivo tabular pequeno para códigos e descoberta de idiomas falados | Inclui países e territórios; coluna de idiomas não é lista de status oficial nem medida de proficiência | Documentação de dumps indica CC BY 4.0; preservar notices do arquivo adquirido | Snapshot opcional do arquivo específico, não `allCountries.zip`; não usar como evidência de `english_official` |
| EF EPI | Candidato a indicador de proficiência; população de testes autoselecionada, sem representatividade garantida | Página consultada da edição 2025 informa 123 países/regiões; não equivale aos 195 Estados | Licença aberta de redistribuição do dataset não foi confirmada; raw data não disponível externamente segundo FAQ | Avaliar metodologia/termos antes de ingestão; atualização por edição, sem preencher países ausentes |
| Dataset local curado | Pode fixar definições e consolidar pequenas evidências revisadas | Cobertura depende das fontes e do esforço de revisão; arquivo local não cria evidência | Manter licença e atribuição por origem; separar fatos, texto e artefatos | Publicar snapshots com manifesto e revisão; corrigir por nova versão, preservando histórico |

Referências diretas da matriz:
[Wikidata P37](https://www.wikidata.org/wiki/Property:P37),
[licenciamento Wikidata](https://www.wikidata.org/wiki/Wikidata:Licensing),
[termos Wikimedia](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use),
[países Natural Earth](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/),
[costa Natural Earth](https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-coastline/),
[termos Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/),
[GeoNames countryInfo](https://download.geonames.org/export/dump/countryInfo.txt),
[documentação de dumps GeoNames](https://download.geonames.org/export/dump/readme.txt),
[edição EF EPI](https://www.ef.com/wwen/epi/) e
[metodologia/FAQ EF EPI](https://www.ef.com/wwen/epi/about-epi/).

Dois pontos precisam ser tratados antes de derivar dados geográficos: Natural
Earth usa fronteiras de facto por padrão, e a camada de costa inclui o Cáspio.
Interseção com costa não pode decidir sozinha a definição do país ou converter
ausência de interseção em false para microestados sem verificar resolução e
mapeamento. Essa política deve ser explícita, testada e versionada.

## Modelo lógico proposto

Separar observação de origem, decisão de curadoria e valor usado no ranking.
Preservar evidências divergentes; escolher uma observação por atributo/país/período
com política explícita. Não usar voto entre agregadores como confirmação independente.

| Registro | Campos propostos |
| --- | --- |
| Catálogo | `attribute_id`, definição, sinônimos, tipo, unidade, escopo, operadores, normalização, fontes admissíveis, política de ausência/validade, versão |
| Fonte/artefato | `source_id`, provedor, URL original, URL/revisão fixa, arquivo local, licença/atribuição, publicação nullable, coleta UTC, revisão/release, SHA-256 dos bytes, extrator/versão e parâmetros |
| Observação | `evidence_id`, ISO alpha-3, atributo, valor bruto tipado/unidade, período/vigência nullable, escopo geográfico, declaração/seção de origem, referências e transformação |
| Valor resolvido | ISO alpha-3, atributo, valor tipado/unidade ou null, `data_status`, motivo, evidências aceitas, decisão/regra de curadoria |
| Manifesto | versões de schema/registro/catálogo/dataset, data de referência, arquivos e hashes, fontes/licenças, versão do código de transformação, parâmetros e relatório de cobertura |

`data_status` proposto: `observed`, `missing`, `conflicting`, `not_applicable` ou
`expired`. Estes estados pertencem aos dados; não substituem os status finais
de país da JEV. Apenas `observed` com valor admissível entra no cálculo inicial.
Uma observação false é dado válido, diferente de missing. Evidência com data de
publicação desconhecida mantém null e motivo; data de coleta não vira publicação.

ISO alpha-3 é a chave de integração; nomes são rótulos. M49 permanece string de
três caracteres. Linguagem e país são entidades distintas; o vínculo Wikidata ↔
ISO deve ser revisado. Não importar todas as entidades rotuladas “país” como registro.

O valor normalizado é calculado usando o catálogo fixado na execução. Se for
materializado no snapshot, precisa identificar essa versão e ser revalidado.
Não persistir um score de afinidade universal: ele depende dos critérios e pesos.

Estrutura de arquivos candidata, **ainda não criada**:

```text
data/affinity/<dataset_version>/
  manifest.json
  criteria.json
  sources.json
  evidence.jsonl
  country_attributes.jsonl
  coverage.json
  raw/                         # apenas arquivos pequenos com reuso permitido
artifacts/data_acquisition/     # staging/cache descartável; nunca fonte única
```

Cada linha JSONL é um registro completo; um índice agrupa múltiplas evidências
por país/atributo. Ordenação e serialização determinísticas facilitam revisão.
O manifesto identifica bytes concretos; uma revisão remota sem cópia preservada
não garante reprodução se o fornecedor retirar o arquivo.

## Obtenção dos dados

Comparação inicial: curadoria manual é adequada à amostra e casos difíceis, mas
precisa registrar o procedimento. Downloads específicos de release funcionam
para geometrias. API estruturada é candidata para idiomas. Scraping de HTML
tem maior fragilidade de extração; dumps globais excedem o recorte necessário.

Fluxo proposto: **adquirir → preservar bruto → extrair → validar → revisar diff
e lacunas → publicar snapshot → consumir localmente**. O conector futuro pertence
à ferramenta de aquisição, sem consulta por pedido ou chamada LLM para obter fatos.

Para Wikidata, descobrir/mapear entidades com consulta restrita e adquirir o
JSON completo com revisão. A interface suporta revisões específicas; JSON de
entidade retém o material para auditar a extração.
[Documentação de acesso](https://www.wikidata.org/wiki/Wikidata:Data_access).
Ranks, qualifiers e referências devem ser tratados explicitamente na política
de seleção; uma declaração histórica ou regional não é automaticamente vigente
e nacional. Ver [statements](https://www.wikidata.org/wiki/Help:Statements) e
[ranking de declarações](https://www.wikidata.org/wiki/Help:Ranking).

Limites iniciais propostos para um futuro piloto, não limites anunciados pelo
fornecedor: um worker, timeout de 30 s por chamada, no máximo duas retentativas,
50 requisições e 20 MiB de respostas descomprimidas por execução. Contar tentativas
no orçamento; baixar geometrias em job com orçamento específico, previamente
dimensionado. Usar User-Agent identificável, cache e `Retry-After`; interromper
ao atingir limite ou receber bloqueio persistente. As orientações do fornecedor
estão na [documentação Wikidata](https://www.wikidata.org/wiki/Wikidata:Data_access).

Falha de rede interrompe a aquisição e preserva o snapshot publicado. Não
substituir dados por zeros nem publicar staging incompleto. `local_only` permite
somente ler ou reconstruir a partir de artefatos locais; não faz downloads.

## Manutenção e publicação

Calendário proposto, sujeito ao piloto: revisar mensalmente alterações de idiomas
oficiais e conflitos; verificar releases geográficos trimestralmente e rever o
mapeamento anualmente; indicadores periódicos acompanham sua edição. Uma mudança
conhecida pode antecipar a revisão. Reconsultar uma fonte não muda a vigência
do fato nem resolve ausência de evidência.

- **Validade:** distinguir período observado, vigência e `last_reviewed_at`.
  Prazo de revisão vencido gera aviso de manutenção; só a política explícita do
  critério determina `expired`. Dados inadmissíveis para o pedido ficam null.
- **Correções:** registrar fonte preferida e motivo por decisão. Fonte oficial
  pertinente e vigente tem prioridade proposta; conflito não resolvido permanece
  `conflicting`. Conservar as observações originais e a trilha de curadoria.
- **Versão:** nunca editar release publicado. Qualquer mudança de valor, fonte,
  escopo ou transformação gera nova versão; catálogo/schema têm versões próprias.
- **Validação:** conferir conjunto do registro, referências, unicidade dos valores
  resolvidos, tipos estritos, unidades, finitude, períodos, licenças e hashes.
  Critérios não habilitados não entram no ranking; ausência não é teste false.
- **Cobertura:** emitir contagens dos cinco `data_status` por critério, com
  denominador 195, e lista de lacunas por país. Também contar observações válidas
  true e false; mostrar cobertura conjunta dos critérios ativos de um pedido.
- **Publicação:** construir em diretório temporário, validar e revisar antes de
  publicar a pasta imutável. Fixar versão explícita ao iniciar uma execução, sem
  trocar dados entre etapas; eventual ponteiro de versão muda atomicamente.
- **Retenção:** manter manifestos e pequenos snapshots publicados no Git; conservar
  todos os artefatos necessários para reproduzir releases mantidos, quando a
  licença permitir. Arquivos maiores exigem arquivo persistente com checksum.
  Cache não referenciado por release pode ser eliminado após 30 dias.
- **Rollback:** selecionar a versão publicada anterior e invalidar cache por
  identidade de dataset/catálogo. Nenhuma recuperação depende de consulta online.

As rotinas acima são propostas; não há scheduler, ingestão ou validação nova
implementados nesta entrega.

## Próximo ensaio e critérios de decisão

1. Alinhar com #14 a semântica dos dois booleanos, o registro e os contratos de
   proveniência. Definir o escopo territorial antes de rotular litoral.
2. Formar amostra de seis países candidatos (`BRA`, `CHE`, `PHL`, `KAZ`, `VAT`,
   `PSE`) para revisar língua, litoral, Cáspio, microestado e mapeamento. A lista
   define casos de investigação, sem afirmar valores ou cobertura.
3. Adquirir apenas o necessário e publicar bruto permitido, hashes, revisão,
   transformação e valores resolvidos; executar uma reconstrução sem rede.
4. Medir cobertura admissível dos 195 por critério, contabilizando lacunas e
   conflitos. Nenhum objetivo de cobertura justifica completar dados artificialmente.
5. Experimentar JSON/JSONL; comparar SQLite no mesmo snapshot apenas se o acesso
   observado exigir consultas/histórico. Registrar medições e custo de manutenção.
6. Revisar a ADR com os resultados; então implementar aquisição/publicação e
   dataset inicial. Qualidade de praia e proficiência exigem investigação própria.

Concluir esta pesquisa inicial não conclui a #13. Permanecem pendentes catálogo
executável, amostra reproduzível, cobertura medida, dataset publicado e integração
com os contratos. As caixas de aceite da issue continuam abertas.
