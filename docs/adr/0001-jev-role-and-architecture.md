# ADR 0001 — JEV como coordenadora de pesquisa e previsão por país

- Data: 02/10/2026.
- Estado: **requisitos funcionais confirmados; arquitetura proposta para implementação**.
- Issue: [#8](https://github.com/felpzw/jev-global-heatmap/issues/8).
- Base de código analisada: `develop`, commit `bc9360b`.
- Escopo desta alteração: documentação; nenhum comportamento de execução alterado.

## Contexto e requisitos confirmados

O responsável definiu que a JEV deve participar da arquitetura com IA, otimizar
as buscas a partir do contexto e retornar a probabilidade de um evento/decisão
nos 195 países do escopo. Em esclarecimento posterior, confirmou que **o usuário
informa o evento e o prazo**. Não cabe à IA escolher esses parâmetros silenciosamente.
A expansão da sigla não foi fornecida, mas não impede definir seu papel funcional.

O escopo é 193 membros da ONU mais os dois Estados observadores. Referências e
mapeamento geográfico estão no [desenho detalhado](../JEV_DESIGN.md).

No código atual, Gemini seleciona um subconjunto de países, produz intensidade
qualitativa e justificativa, Pydantic valida estrutura e Plotly apresenta o mapa.
Não há pesquisa em fontes, estimador probabilístico, cobertura obrigatória dos
195 países ou motor JEV independente. O objetivo novo exige evolução explícita.

## Decisão arquitetural proposta

Adicionar a JEV como serviço de aplicação no próprio projeto, acima dos adaptadores
de IA local/cloud. Ela será responsável por validar o pedido, planejar a pesquisa,
obter evidências, distribuir inferência em lotes, controlar orçamento/retomada e
reconciliar os resultados com o registro versionado dos 195 Estados.

Manter as camadas interface → serviços → validação → visualização. Aproveitar o
renderer e o gerenciamento de sessão, adaptando-os para probabilidade, status por
país e proveniência. A seleção de provedor continua no escopo da #10.

Usar contrato novo e versionado de previsão, separado de `HeatmapResponse`.
`heat_score` não será rebatizado nem convertido em probabilidade: os dados legados
continuam identificados como intensidade qualitativa.

A resposta representará todos os 195 Estados exatamente uma vez, com número em
[0, 1] quando houver estimativa justificável, ou `null` e status explícito para
insuficiência de evidência, não aplicabilidade ou erro técnico. Isso preserva
cobertura sem inventar precisão. Com erro técnico, a execução é identificada como
parcial; a existência de 195 registros não significa 195 inferências bem-sucedidas.

## Alternativas

| Alternativa | Vantagem | Limitação | Encaminhamento |
| --- | --- | --- | --- |
| Apenas pedir 195 países ao Gemini | Alteração pequena de prompt | Não garante cobertura, fontes, probabilidade ou retomada; saída atual limitada a 8.192 tokens | Rejeitar como solução completa |
| Manter o MVP sem JEV | Simplicidade e regressões já testadas | Não atende à finalidade confirmada | Preservar somente como fluxo legado durante a migração |
| JEV modular dentro da aplicação | Reutiliza arquitetura e permite fontes, contratos, lotes e provedores independentes | Aumenta responsabilidades e exige avaliação nova | Recomendada |
| Novo microserviço JEV com filas distribuídas | Escala e isolamento operacional | Complexidade sem volume/requisitos operacionais demonstrados | Adiar até haver necessidade medida |

## Contratos e pontos de integração

- UI → JEV: contexto, evento, prazo, regra observável de resolução, data de referência,
  modo de evidências e provedor/modelo.
- JEV → registro: conjunto fixo e versionado, não uma lista gerada pela LLM.
- JEV → busca: consultas por evento/país; retorno de material recuperado com fonte,
  datas e identificadores verificáveis. Documentos locais e busca externa são modos distintos.
- JEV → estimador/adaptador: subconjunto de países, evidências e contrato estruturado.
  Capacidade de contexto/schema e término normalizado dependem de cada provedor.
- JEV → UI: 195 registros reconciliados, status da execução, fontes e metadados completos.
- Visualização: porcentagem somente para probabilidades estimadas; nulos e países
  fora do escopo têm identificação própria. Tabela/busca asseguram acesso a microestados.

Campos e invariantes estão em [JEV_DESIGN.md](../JEV_DESIGN.md), que também define
cache, retomada, migração e sequência de implementação.

## Consequências e avaliação

Há maior rastreabilidade e controle de cobertura, mas também mais chamadas, fontes
e estados de execução. Redução de custo/tempo precisa ser demonstrada por benchmark;
usar lotes ou modelo local não prova otimização por si só.

A primeira versão pode produzir estimativas assistidas por LLM explicitamente não
calibradas. Alegações de capacidade probabilística exigem eventos resolvidos,
separação temporal, comparação com baseline, Brier/log loss e curvas de confiabilidade.
Fontes corretas e JSON válido, isoladamente, não comprovam qualidade preditiva.

A validade do contrato deve cobrir 100% dos cenários de cobertura/invariantes;
qualidade, latência e custo terão protocolos e limiares definidos antes do ensaio
correspondente. Reaproveitar a infraestrutura da #4, mantendo sua avaliação de
prompts e acrescentando avaliação própria de previsão, sem confundir as duas.

## Evidências e próximos passos

A revisão anterior do mesmo código executável aprovou 29 testes e quatro fixtures
offline. Nenhuma geração real, teste de pesquisa ou calibração foi executado nesta
alteração documental. Essas evidências cobrem o MVP, não a arquitetura proposta.

Implementar em sequência: registro/contratos → adaptadores #10 → evidências e
orquestração JEV → UI/mapa/exportação → avaliação probabilística e operacional.
O backlog detalhado acompanha a issue #8 e o desenho técnico.

O bloqueio anterior por falta de definição funcional foi resolvido. A #8 continua
aberta para consolidar a proposta/documentação no PR #11 e acompanhar a decomposição
das entregas. Seu encerramento futuro significará conclusão da análise, não que a
JEV já esteja operando ou que todos os critérios preditivos tenham sido demonstrados.
