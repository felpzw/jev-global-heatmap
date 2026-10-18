# JEV Global Heatmap — kit para portfólio e LinkedIn

Preparado em 18/10/2026. Texto editável; nenhuma publicação foi realizada.

Dados da demonstração salvos: [resumo com os cinco primeiros e seus fatores](evaluations/showcase_summary.json)
e [ranking dos 195 em CSV](evaluations/showcase_ranking.csv). Reproduzir com
`python -m scripts.export_showcase`; o JSON completo fica em `artifacts/showcase_result.json`.

## Narrativa do projeto

Como transformar uma intenção em um resultado global que possa ser inspecionado?
O projeto organiza um pedido em critérios, aplica filtros e pesos sobre evidências
versionadas e mostra a afinidade em um mapa mundial. O Gemini é uma etapa opcional
de explicação dos resultados selecionados. Scores e ordem são responsabilidade
do motor local JEV, que funciona sem credenciais.

Competências demonstradas: arquitetura com responsabilidades separadas, contratos
Pydantic estritos, pipeline de dados reproduzível, tratamento explícito de lacunas,
visualização Plotly, estado e cancelamento no Streamlit, integração Gemini com
contexto restrito, testes de falhas, avaliação de ranking e CI sem credenciais.

## Números publicáveis e limites

| Informação | Evidência | Como apresentar |
| --- | --- | --- |
| 195 Estados, 193 membros + 2 observadores | `data/country_registry.json` | Cobertura do registro, não garantia de dados completos |
| 390 posições país/critério | `data/affinity/v1/evidence.jsonl` | Inclui evidências ausentes |
| Litoral: 195/195; idioma: 133/195; 62 lacunas | `data/affinity/v1/coverage.json` | Snapshot histórico; não validação factual atual |
| Até 20 candidatos e 10 justificativas | Contratos e testes do motor | Limites funcionais; não parâmetros otimizados |
| Recall 1,0; precision@3 0,722; NDCG@3 1,0 | `docs/evaluations/affinity_offline.json` | Somente fixtures sintéticas de teste; conjunto pequeno |
| Latências p50/p95 locais | Mesmo relatório, com ambiente e repetições | Medição desta máquina; não benchmark de produção |
| Custo e tokens Gemini | Não medidos | Não divulgar porcentagem de economia ou ganho de qualidade |

O conjunto local tem dois critérios booleanos. Scores são discretos e há muitos
empates; o desempate ISO é estável, sem significado de mérito. Não chamar o sistema
de interpretação universal, previsão probabilística ou recomendador de viagem.
O mapa exige CDN no navegador; `local_only` descreve o motor e as explicações.

## Roteiro de vídeo — 60 a 90 segundos

1. **0–10 s:** “E se uma ideia virasse um mapa explicável?” Mostrar a interface e
   o pedido “Prefiro litoral e inglês oficial”.
2. **10–25 s:** Rever os dois critérios e alterar o peso do litoral para 3. Explicar
   que o score vem de regras e evidências, com confirmação do pedido.
3. **25–40 s:** Calcular. Mostrar 195 registros, cores, candidatos destacados e
   países sem dados completos. Usar hover e ranking.
4. **40–55 s:** Abrir Critérios e fontes e inspecionar um país. Mostrar peso,
   contribuição e proveniência. Buscar um microestado na tabela.
5. **55–70 s:** Trocar para “Prefiro países sem litoral” e recalcular. Mostrar que
   a mudança do conceito muda o ranking sem enviar o mundo inteiro à LLM.
6. **70–90 s:** Mostrar JSON exportável e arquitetura. Encerrar com o limite atual:
   catálogo pequeno e dados históricos; próximos passos são ampliar critérios
   e realizar avaliação humana e ensaio Gemini com credenciais.

Para capturas, manter o aviso de snapshot visível e usar apenas dados do projeto.
Uma revisão no Safari confirmou a renderização do mapa e os controles básicos;
a captura final para redes deve ser feita com o enquadramento desejado.

## Rascunho de publicação

Uma ideia pode virar um mapa mundial explicável?

No JEV Global Heatmap, um pedido como “prefiro litoral e inglês oficial” vira
critérios que o usuário revisa, pondera e confirma. A JEV aplica os requisitos e
calcula a afinidade de forma determinística. O resultado aparece em um mapa,
com ranking, fatores, fontes e exportação JSON.

O registro cobre 195 Estados. Ausência de dados aparece como ausência; um país
excluído por requisito também fica identificado. Quando habilitado, o Gemini
recebe somente os selecionados para explicar o resultado. O motor funciona sem
chave, com justificativas locais por template.

Usei Python, Pydantic, Streamlit e Plotly para explorar essa separação entre
interpretação de critérios, ranking e explicação. O catálogo inicial tem dois
atributos e usa um snapshot histórico com proveniência. A avaliação funcional
em dados sintéticos está publicada; qualidade em consultas reais e custo de API
ainda exigem ensaio próprio.

O próximo passo é ampliar os conceitos com fontes comparáveis e avaliar os
resultados com usuários. Em qual domínio essa abordagem seria útil para você?

Código: https://github.com/felpzw/jev-global-heatmap/tree/develop

#Python #EngenhariaDeSoftware #InteligenciaArtificial #DataVisualization #Portfolio

## Descrição curta para portfólio

Aplicação de busca conceitual global com mapa de afinidade, critérios revisáveis
e evidências rastreáveis. Motor JEV determinístico, registro de 195 Estados,
ranking por pesos e explicação Gemini opcional restrita aos selecionados.
Inclui testes offline, reprodução do dataset e avaliação funcional publicada.
