# Plano de implementação da JEV — revisão da issue #8

> Snapshot histórico substituído pela ADR 0002 em 05/10/2026. Estados e planos abaixo não são o backlog atual.
Revisão em 05/10/2026, na branch `docs/issue-8-jev-architecture`, commit
`1612f69`. Plano proposto; nenhuma funcionalidade JEV foi implementada nesta revisão.

## Situação e escopo

A [issue #8](https://github.com/felpzw/jev-global-heatmap/issues/8) trata da análise
arquitetural. Sua definição funcional está confirmada e a pendência registrada é
consolidar e integrar o [PR #11](https://github.com/felpzw/jev-global-heatmap/pull/11).
Na consulta desta revisão, o PR está aberto, em draft e ainda não integrado à
`develop`. A documentação já existe na branch local. Concluir a #8 não comprova
que a JEV está executando: as entregas abaixo precisam de acompanhamento próprio.

O código permanece Streamlit → Gemini → `HeatmapResponse` → Plotly. O prompt
prefere até 40 países, a resposta aceita até 249 países/territórios, o contexto
tem limite de 4.000 caracteres e a saída de 8.192 tokens. Não há registro dos
195, pesquisa em fontes, previsão probabilística, adaptadores ou checkpoints.
Os 29 testes offline passaram nesta revisão; validam o MVP e usam simulações,
sem chamadas reais ao provedor ou avaliação factual da futura JEV.

Este plano detalha o [desenho técnico](JEV_DESIGN_LLM.md) e a
[ADR 0001](../adr/0001-jev-role-and-architecture.md), sem substituir seus contratos.

## Requisitos organizados

| ID | Requisito | Verificação de aceite |
| --- | --- | --- |
| R1 | Usuário informa contexto, evento observável, prazo e regra de resolução; execução registra `as_of` | Pedido incompleto, contraditório ou prazo anterior à referência não inicia inferência; ambiguidade exige esclarecimento |
| R2 | Registro versionado dos 193 membros + dois observadores, com ISO alpha-3/M49 e fontes | Conjunto completo revisado contra fontes oficiais; exatamente 195 códigos únicos, incluindo `VAT` e `PSE` |
| R3 | Novo contrato versionado, separado de intensidade qualitativa | Probabilidade finita em [0,1] somente em `estimated`; demais estados com `null`; nenhum score legado convertido |
| R4 | Evidências recuperadas e rastreáveis por país | Toda estimativa referencia material existente, pertinente ao país/evento, com origem, trecho/hash e datas; referências inexistentes são rejeitadas |
| R5 | JEV planeja pesquisa, executa lotes e reconcilia o conjunto fixo | País omitido, extra ou duplicado não passa silenciosamente; resultado final representa cada Estado uma vez |
| R6 | Execução tem limites, identidade e retomada | Timeout, truncamento, retry e cancelamento não misturam execuções; erros remanescentes identificam resultado parcial |
| R7 | Inferência e modo de evidências são escolhas distintas | `local_only` não consulta buscador externo; modelo local não faz fallback cloud |
| R8 | Mapa, tabela e exportação preservam a semântica | Percentual somente para estimativas; nulos/status explícitos; acesso aos 195, incluindo microestados; JSON com pedido, fontes e versões |
| R9 | Preservar o MVP durante a migração | Demonstração, reruns, resultado anterior e fluxo legado continuam cobertos pelos testes |
| R10 | Qualidade e otimização são medidas | Primeira previsão marcada como não calibrada; benchmark reproduzível e avaliação contra baseline antes de alegar ganhos |

Validar estrutura de um evento não prova que sua resolução seja objetiva. A UI
deve permitir revisar a formulação; uma sugestão da IA precisa ser aceita pelo
usuário antes de virar o evento usado nos 195 países.

## Entregas e dependências

| Etapa | Atividades e arquivos previstos | Dependências / saída verificável |
| --- | --- | --- |
| 0 — Consolidar análise | Revisar ADR/desenho/plano, retirar draft e integrar PR #11 conforme fluxo do projeto | Critérios documentais da #8; integração ainda pendente |
| 1 — Fundação | `data/countries_un195.json`, `country_registry.py`, `forecast_schema.py`, fixtures e testes | Independente de Docker e API; pedido/evidências/resultado validados com conjunto exato |
| 2 — Provedores | Interface de geração estruturada e adaptador Gemini; capacidades, erros e término normalizados | Fundação; alinhamento com #10 para reutilizar interface e adicionar runtime local |
| 3 — Evidências | `evidence_service.py`, importação local, deduplicação, relevância e corte temporal; posteriormente conector externo | Contrato de evidências; fontes reais rastreáveis sem URLs inventadas pela LLM |
| 4 — Serviço JEV | `forecast_estimator.py`, `jev_service.py`, lotes, orçamento, reconciliação, cache/checkpoints | 1–3; execução com adaptador simulado antes de integração real; todos os status exercitados |
| 5 — Produto | Formulário, progresso, apresentação parcial, mapa de probabilidades, tabela e exportação | Serviço reconciliado; preservação da sessão e acesso aos 195 |
| 6 — Avaliação | Benchmark operacional, revisão de fontes, eventos resolvidos/prospectivos e baseline | Fluxo integrado; limites e protocolo definidos antes do ensaio |

A sequência é lógica, mas a fundação pode começar enquanto o PR documental é
consolidado. A #10 é responsável por Docker, runtime local e aba de modelos.
Sua conclusão integral não precisa bloquear uma primeira integração Gemini:
o requisito é compartilhar um contrato de adaptador adequado à JEV e ao legado.
A #4 continua tratando dos prompts qualitativos atuais.

## Primeira entrega recomendada: fundação offline

1. Construir e revisar o registro oficial, com versão, fontes e data de consulta.
   Não derivar o universo de países de uma resposta da LLM ou do catálogo inteiro
   de `pycountry`. Guardar M49 como código de três caracteres, preservando zeros.
2. Implementar carregamento e validação do registro, incluindo unicidade e
   correspondência entre códigos/nome/condição de membro ou observador.
3. Implementar `ForecastRequest`, `Evidence`, `CountryForecast` e
   `ForecastResponse`, com versão de schema, pedido original, identidade da
   execução e versão do registro. Definir resposta de lote separada da resposta
   final: um lote contém apenas seu subconjunto; a reconciliação exige os 195.
4. Definir metadados de execução: provedor/modelo, versão/hash do prompt, método,
   estado de calibração, instantes e contadores de status/falhas.
5. Criar fixtures explicitamente fictícias com estimativas, insuficiência,
   inaplicabilidade e erro. Não usar fixtures como evidência de capacidade preditiva.
6. Testar conjunto incorreto mesmo com 195 registros, duplicatas, extras, nulos,
   NaN/infinito, booleanos/strings como probabilidade, datas inválidas e referências
   de evidências inexistentes ou incompatíveis. Definir deliberadamente a leitura
   de datas ISO no JSON sem afrouxar os demais tipos.

Aceite: suíte offline aprovada; contrato final com cobertura exata, fixtures
serializáveis e rejeições demonstradas; nenhum acoplamento a SDK, Docker ou UI.
Esta entrega não precisa gerar previsões nem mudar o mapa.

## Decisões ainda necessárias

As decisões abaixo são propostas para discussão, não requisitos já confirmados.
Elas não impedem iniciar registro e contratos.

| Decisão | Proposta inicial | Quando precisa estar fechada |
| --- | --- | --- |
| Primeiro recorte de evidências | Começar com documentos locais/importados; habilitar busca externa em entrega posterior | Antes do serviço de evidências |
| Busca externa | Selecionar conector, fontes aceitas, credenciais, limites e política de atualização | Antes de implementar `external_search` |
| Operação do evento | Formulário explícito com regra de resolução e revisão de ambiguidades | Antes da interface JEV |
| Orçamento | Configurar tamanho de lote, concorrência, timeout, tentativas e teto por execução; medir antes de fixar valores de produção | Antes da execução integrada |
| Retomada e cache | Repositório local com isolamento por sessão, chave completa do pedido/versões e gravação atômica; definir expiração e retenção | Antes de persistir contextos/evidências |
| Provedor inicial | Usar Gemini existente por adaptador; adicionar local pelo escopo #10 | Antes do primeiro ensaio real |
| Qualidade mínima | Definir domínio inicial, baseline, conjunto de avaliação, limiares e tamanho da amostra | Antes de alegar qualidade preditiva ou calibração |

## Riscos e tratamento

- **Falsa precisão:** permitir abstenção e identificar estimativas não calibradas.
- **Cobertura aparente:** validar igualdade de conjuntos, além do comprimento;
  distinguir erros técnicos de ausência de evidência.
- **Saída truncada e contexto excessivo:** selecionar evidências e limitar lotes
  segundo capacidades do modelo; rejeitar geração incompleta.
- **Fontes frágeis ou conteúdo instrucional:** tratar material recuperado como
  dados, registrar proveniência e submeter pertinência factual à revisão.
- **Vazamento temporal:** filtrar material por `as_of`, registrar versão do modelo
  e arquivar previsões prospectivas antes de seus desfechos.
- **Geometria incompleta:** conferir cobertura visual e oferecer tabela/busca ou
  marcadores sem atribuir o resultado de microestados a seus vizinhos.
- **Custo/latência desconhecidos:** medir execução real e cache no mesmo workload;
  testes simulados não comprovam redução de custo nem velocidade.

## Próximo passo concreto

Iniciar a etapa 1 em uma branch de implementação a partir da base definida pelo
fluxo do projeto. Após o aceite offline, integrar adaptador e evidências para uma
primeira execução rastreável. Decompor as demais entregas em acompanhamento próprio
sem ampliar implicitamente a #8, a #10 ou a #4. Este plano não abriu novas issues,
alterou o GitHub, integrou o PR ou iniciou implementação executável.
