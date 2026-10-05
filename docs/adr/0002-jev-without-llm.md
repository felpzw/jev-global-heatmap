# ADR 0002 — JEV com dados e estimador independente de LLM

- Data: 05/10/2026.
- Estado: decisão de escopo; execução ainda não implementada.
- Substitui: ADR 0001 e backlog associado a LLM.

## Decisão

Separar a documentação e implementação da JEV do MVP Gemini. O fluxo novo usa
entrada estruturada, conectores/datasets, normalização e estimador estatístico
por domínio, sem chamadas de LLM. A JEV continua serviço no processo da aplicação,
coordenando os 195 Estados, status, evidências, limites e reconciliação.

## Motivo e consequências

O usuário solicitou arquitetura apenas com JEV após analisar alternativas sem
LLM. É possível obter dados e estimar eventos com algoritmos próprios, mas isso
exige domínio, fontes e método definidos. A flexibilidade de texto livre é
substituída inicialmente por catálogo de eventos/indicadores suportados.

Wikipedia/Wikidata, APIs oficiais e datasets locais serão avaliados em issue
própria; banco e fonte não são pré-selecionados. Docker de modelos e tuning de
prompts deixam o backlog ativo. Preservar histórico e pendências sem declarar
ensaios ou implementações antigos concluídos.

A ADR 0001 permanece histórica. Registro dos 195, separação score/probabilidade,
abstenção, proveniência e avaliação temporal permanecem requisitos. A migração
executável é posterior; README deve distinguir código atual e objetivo novo.
