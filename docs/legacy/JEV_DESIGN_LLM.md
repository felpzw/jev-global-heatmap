# JEV: pesquisa e probabilidade de eventos em 195 países

> Snapshot histórico substituído pela ADR 0002 em 05/10/2026. Estados e planos abaixo não são o backlog atual.
Estado: proposta de implementação da issue #8, com finalidade e entrada confirmadas
pelo responsável em 02/10/2026. Este documento não altera o código de execução.

## 1. Objetivo e entrada

JEV será a camada de aplicação com IA responsável por transformar um pedido de
pesquisa em buscas, evidências e estimativas por país, garantindo cobertura do
universo definido. **O usuário fornece evento e prazo.** A interface mantém o
contexto livre e acrescenta esses campos obrigatórios.

Para estimar uma probabilidade, o evento deve ter resultado observável. “Carros
elétricos” é um tema; “a participação de veículos elétricos nas vendas anuais de
automóveis novos atingir pelo menos X% até a data Y” é um evento verificável.
Métrica, limiar, população/unidade e regra de resolução precisam estar claros.
Se o evento for uma decisão de uma organização, identificar também o decisor.
Datas ambíguas, prazo anterior à data de referência ou contexto que contradiga o
evento exigem esclarecimento antes da geração, sem preencher campos por suposição.

O sistema aceitará temas diversos, mas “qualquer input” não significa que qualquer
texto permita uma probabilidade defensável. Pedidos vagos retornam orientação;
eventos sem evidência ou inaplicáveis a um país retornam status explícito.

Definição de saída: `P(evento ocorrer em c até T | evidências disponíveis em t0)`.
`t0` é a data de referência da previsão; `T` é o prazo fornecido pelo usuário.
O critério de resolução deve explicar como verificar ocorrência ou não ocorrência
após T. O número apoia uma decisão; não determina sozinho qual ação é melhor.

## 2. Universo geográfico

Adotar uma lista versionada com os [193 membros da ONU](https://www.un.org/en/about-us)
e os [dois Estados observadores](https://www.un.org/en/about-us/non-member-states):
Santa Sé e Estado da Palestina. São 195 Estados no escopo, e não 195 membros.
O mapeamento ISO/M49 usa a [tabela da UNSD](https://unstats.un.org/unsd/methodology/m49/overview/):
Santa Sé → `VAT`, Palestina → `PSE`.

Proposta: `data/countries_un195.json`, com versão/data de consulta, fontes,
nome, ISO alpha-3, M49 e condição de membro/observador. Construir a lista a partir
da membresia e dos observadores; a M49 inclui outros territórios e não deve ser
usada inteira como se tivesse só 195 entradas. Não pedir à LLM que invente a lista.

Validação global: `set(resultado.iso_alpha_3) == set(registro.iso_alpha_3)`,
195 entradas e nenhuma duplicata. Só validar comprimento ou existência no
`pycountry` não basta. Mudanças futuras na composição exigem uma nova versão do
registro, com migração deliberada, preservando a referência das execuções antigas.

Cobertura do contrato e cobertura gráfica são diferentes: confirmar presença de
todos os códigos nas geometrias e dar acesso por tabela/busca e, quando necessário,
marcadores aos microestados pouco visíveis. Nunca atribuir a um vizinho a estimativa
de um país por falta de polígono. Territórios fora do escopo precisam de identificação
distinta dos países do escopo com evidência insuficiente.

## 3. Responsabilidades propostas

| Módulo proposto | Responsabilidade | Dependência |
| --- | --- | --- |
| `src/services/jev_service.py` | Validar pedido, planejar, dividir trabalho, reconciliar resultados e relatar progresso | Contratos, registro, busca, estimador e adaptadores |
| `src/services/country_registry.py` | Carregar o universo de 195 Estados e verificar cobertura exata | Registro versionado |
| `src/services/evidence_service.py` | Recuperar, deduplicar e selecionar evidências pertinentes ao evento e país | Fontes locais/importadas e conectores de busca habilitados |
| `src/services/providers/` | Executar pedidos estruturados via Gemini ou runtime local; normalizar término e erros | Evolução já prevista na #10 |
| `src/services/forecast_schema.py` | Pedido, evidências e resposta de probabilidades com invariantes | Pydantic; separado do schema legado |
| `src/services/forecast_estimator.py` | Estimar a probabilidade com método e versão identificados | Modelo escolhido, evidências e eventual calibrador validado |
| `src/app.py` | Coletar evento/prazo, seleção de provedor, progresso, mapa/tabela/exportação | Serviço JEV; sem detalhes específicos de SDK |

São módulos sugeridos, não arquivos já implementados. A JEV permanece no processo
da aplicação inicialmente; o Docker da #10 hospeda o runtime local. Persistência
de resultados/checkpoints usa um repositório local simples na primeira etapa,
com identificação por execução, sem exigir banco distribuído ou filas externas.

## 4. Busca, evidências e controle da inferência

1. Validar contexto, evento, prazo e regra de resolução. Registrar t0 e os 195 países.
2. Preparar consultas por evento/país e critérios de relevância, mantendo o mesmo
   evento em todos os países. Evidência global pode ser compartilhada, mas seu
   uso para um país precisa ser justificado.
3. Recuperar fontes e registrar conteúdo/trecho, endereço ou identificador local,
   origem, data de publicação e coleta, país e hash do material usado. A IA pode
   sugerir consultas, mas não criar fontes que o serviço não recuperou.
4. Excluir informação posterior a t0 em avaliações históricas. Deduplicar fontes
   e distinguir cópias de evidências independentes. Conteúdo recuperado é dado,
   não instrução para modificar o contrato de geração.
5. Selecionar evidências pertinentes dentro do limite de contexto do provedor.
   Informar ausência, contradição e desatualização; não preencher lacunas com zero.
6. Estimar em lotes de tamanho configurável e validar cada resultado. Concorrência,
   timeout, tentativas e orçamento total devem ter limites explícitos por provedor.
7. Reconciliar todos os lotes com o registro. Retentar somente itens falhos quando
   cabível; não duplicar países nem esconder truncamentos. Preservar checkpoints
   para retomada do mesmo pedido e da mesma versão de evidências.
8. Publicar o novo resultado após reconciliação, com status por país e contadores.
   Se houver erros técnicos remanescentes, o conjunto é identificado como parcial,
   mesmo contendo 195 registros. O resultado anterior fica disponível e separado;
   cancelar não mistura previsões de execuções distintas.

Cache deve incluir evento, contexto, prazo, t0, país, versões de fonte/registro,
provedor, modelo e prompt. Evidências dinâmicas têm validade definida. A reutilização
precisa respeitar o isolamento dos dados da sessão. Benchmark medirá o efeito de
cache, lote e concorrência; a redução de custo/tempo é uma hipótese a verificar.

Não é adequado apenas substituir “40” por “195” no prompt: o cliente atual tem
limite de saída de 8.192 tokens, não controla cobertura e não retoma respostas
parciais. O lote precisa caber também na janela de contexto do modelo local.

Modos propostos de evidência: `local_only` (documentos locais/importados, sem busca
externa durante a execução) e `external_search` (conectores habilitados). A seleção
de um LLM local não autoriza implicitamente enviar o contexto a um buscador externo.
Em ambos os modos, o método deve declarar as evidências efetivamente disponíveis.

## 5. Contratos propostos e migração

Usar um contrato novo, com `schema_version`, sem trocar o significado de `heat_score`.

| Estrutura | Campos mínimos propostos |
| --- | --- |
| `ForecastRequest` | `context`, `event`, `deadline`, `resolution_rule`, `as_of`, `evidence_mode`, provedor/modelo |
| `Evidence` | `evidence_id`, país(s), fonte local/URL, trecho e hash, datas de publicação/coleta |
| `CountryForecast` | `iso_alpha_3`, `probability`, `status`, `rationale`, `evidence_ids`, `method`, `calibration_status` |
| `ForecastResponse` | `schema_version`, `run_id`, pedido original, versão do registro, metadados de execução, catálogo de evidências e `countries` |

`probability` é número finito entre 0 e 1 ou `null`. Estados propostos:

| `status` | Probabilidade | Significado |
| --- | --- | --- |
| `estimated` | Obrigatória, em [0, 1] | Estimativa com método e evidências identificados; não implica calibração comprovada |
| `insufficient_evidence` | `null` | Evidência insuficiente para uma estimativa justificável |
| `not_applicable` | `null` | Evento não se aplica ao país; exige justificativa |
| `error` | `null` | Falha técnica após política de tentativas; não é conclusão sobre o país |

Validação rejeita chaves/códigos indevidos, duplicatas, números fora do intervalo,
combinações inválidas entre status e probabilidade e IDs de evidência inexistentes
ou inadequados ao país. Zero e um são permitidos estruturalmente, mas exigem revisão
de sua justificativa; não usar valores extremos para representar incerteza.

Os 195 países estarão sempre representados no resultado reconciliado. Exigir 195
números mesmo sem evidência criaria falsa precisão. Se for desejada uma previsão
baseada em prior para casos sem dados específicos, ela precisará de uma política
metodológica explícita e validação; não entra como fallback oculto nesta proposta.

O mapa futuro colore `100 * probability` apenas para `estimated`, com legenda
“Probabilidade estimada (%)”. Nulos não passam pelo schema legado como zero.
Tabela, tooltip e exportação incluem status, método, fontes e indicação de calibração.
O JSON completo preserva evento/prazo, referência temporal, versões, provedor/modelo,
hash/versão do prompt, fontes e falhas. Eventos entre países não são alternativas
mutuamente exclusivas: suas probabilidades não precisam somar 1.

Manter o fluxo legado enquanto o novo é validado. Resultados antigos continuam
identificados como intensidade qualitativa; não se converte score em probabilidade
dividindo por 100. Um adaptador de visualização pode compartilhar layout e controles,
mas deverá aceitar a nova semântica e os estados nulos explicitamente.

## 6. Método probabilístico e avaliação

Primeira entrega possível: previsão assistida por LLM, condicionada a evidências,
explicitamente marcada como **estimativa não calibrada**. Resposta numérica em JSON
ou segurança verbal do modelo não é demonstração de probabilidade calibrada.
Intervalos de confiança também não devem ser produzidos sem método definido.

Para demonstrar capacidade preditiva, montar eventos históricos com resolução
observável, fontes existentes na data de referência e separação temporal entre
desenvolvimento, calibração e teste. Conhecimento posterior embutido no próprio
modelo também pode contaminar retrospectivas; registrar versão/data do modelo
e complementar com previsões prospectivas arquivadas antes dos desfechos.

Comparar com baseline simples de taxa-base/prior definido pelo domínio e mantido
igual entre métodos. Usar Brier score, log loss e curvas de confiabilidade; Brier
sozinho não isola calibração. Ver a [documentação de calibração](https://scikit-learn.org/stable/modules/calibration.html).
Não adicionar scikit-learn como dependência só por esta proposta documental.

Relatar número de previsões resolvidas, cobertura de estimativas, abstenções, erros
técnicos, desempenho por domínio/região e incerteza das métricas. Os 195 resultados
de um único evento não formam automaticamente 195 observações independentes;
considerar dependências por evento/tempo na avaliação. Comparar métodos no mesmo
conjunto e mostrar cobertura, evitando ganhos artificiais por omitir casos difíceis.

Critérios propostos:

- Contrato: cobertura exata dos 195, unicidade e invariantes em 100% dos testes.
- Proveniência: toda estimativa referencia evidências recuperadas e a execução.
- Semântica: evento, prazo e regra de resolução inalterados entre países/lotes.
- Resiliência: testes de truncamento, timeout, retomada, cache e modelo local
  indisponível, sem encaminhamento automático a cloud nem mistura de execuções.
- Desempenho: medir p50/p95, tempo até primeiro lote, tempo total, custo/tokens quando
  disponíveis e recursos locais. Comparar execução sem otimizações e com cache/lotes
  sob o mesmo workload; definir orçamento/limites antes do ensaio de aceite.
- Qualidade: não promover a alegação de “probabilidades calibradas” até haver
  protocolo com amostra, limiares e intervalos de avaliação definidos antes do teste
  e resultados fora da amostra. Enquanto isso, manter o rótulo experimental.

A #4 mantém a comparação dos prompts existentes. Avaliação probabilística é uma
etapa nova: reaproveita a infraestrutura, mas não pode usar dispersão de scores
ou apenas validade ISO como critério de sucesso.

## 7. Sequência de implementação

1. **Fundação:** registro dos 195 Estados e contratos versionados, com testes de
   igualdade do conjunto, status, evento/prazo e referências de evidência.
2. **Adaptadores (#10):** capacidades de schema/contexto/término por provedor e
   seleção local/cloud; preservar o fluxo legado durante a migração.
3. **Busca e serviço JEV:** evidências inicialmente locais/importadas e conectores
   externos explicitamente configurados; estimativa em lotes, orçamento e retomada.
4. **Interface e mapa:** formulário de evento/prazo, progresso, tratamento de nulos,
   acesso a todos os 195, microestados, tabela e exportação com proveniência.
5. **Avaliação:** benchmark de busca/execução, revisão de fontes e conjunto de
   previsões resolvidas/prospectivas antes de alegar qualidade probabilística.

O fechamento da análise arquitetural #8 não significa implementação dessas etapas.
A confirmação do papel da JEV já foi obtida; a consolidação da ADR/documentação e
o acompanhamento das entregas continuam necessários.
