# ADR 0001 — Papel da JEV e limites da arquitetura

- Data: 02/10/2026.
- Estado: **proposta; definição de JEV pendente de confirmação**.
- Issue: [#8](https://github.com/felpzw/jev-global-heatmap/issues/8).
- Base analisada: `develop`, commit `bc9360b`.
- Escopo desta alteração: documentação; nenhum comportamento de execução alterado.

## Contexto e definição pendente

O repositório chama o produto de JEV Global Heatmap, sem expandir a sigla nem
definir uma metodologia ou mecanismo JEV. As ocorrências no código estão no
título da aplicação, identificação do pacote e nome do arquivo exportado.
Não existe uma implementação independente de JEV que possa ser descrita como
motor próprio. O mecanismo observado é o pipeline Gemini → validação → mapa.

Essa constatação não define a intenção do produto. É necessário confirmar com o
responsável o significado de JEV, sua finalidade, casos de uso, eventuais regras
de domínio e referências. Nenhuma expansão da sigla ou referência externa é
adotada por semelhança de nome.

## Evidências do funcionamento atual

| Pergunta | Evidência |
| --- | --- |
| Quem interpreta o tema? | Gemini recebe o texto do usuário e `SYSTEM_PROMPT` por `generate_heatmap` |
| Quem escolhe os países? | O modelo, orientado a omitir países sem suporte e preferir até 40 entradas |
| Quem atribui o score? | O modelo; o código não aplica fórmula ou normalização estatística |
| Quem justifica os scores? | O mesmo modelo, em `context_summary`, sem citações verificadas |
| Quem valida? | O cliente verifica conclusão com `STOP`; Pydantic valida estrutura, ISO e limites |
| Quem apresenta? | Streamlit mantém o estado; Plotly usa diretamente os scores validados |
| Como a demonstração funciona? | Uma fixture fictícia validada substitui a chamada à LLM |
| Há motor JEV separado? | Não foi encontrado em `src/`; o significado do nome continua pendente |

O contrato público permanece `HeatmapResponse` com `countries`, contendo
`iso_alpha_3`, `heat_score` e `context_summary`. Ausência de país é ausência de
informação; zero é um score válido. Resultados vazios válidos substituem o mapa;
falhas preservam o resultado anterior e seu contexto.

## Adequação e lacunas

| Critério | Situação observada | Consequência |
| --- | --- | --- |
| Qualidade | Prompt orienta a análise; schema valida estrutura | Validade do JSON não demonstra precisão factual |
| Rastreabilidade | Sessão guarda contexto e origem; download só contém países | Falta identificação completa de uma execução exportada |
| Testabilidade | Renderer puro, schema compartilhado, cliente e UI testados com simulação | Boa cobertura do contrato; não comprova qualidade real do Gemini |
| Acoplamento | UI chama um cliente específico Gemini | Adaptadores são justificados para a alternância local/cloud da #10 |
| Latência | Uma chamada síncrona, timeout de 60 s, sem retry automático | Latência real do provedor ainda precisa ser medida pela #4 |
| Custo | Geração só no envio; reruns reutilizam estado e figura | Não há medição de tokens/custo por pesquisa no app |
| Manutenção | Poucas camadas e um contrato comum | Separar provedores preserva simplicidade; serviços extras exigem motivação |

O uso atual se aproxima de uma ferramenta de exploração geográfica qualitativa.
Não há dados suficientes para atribuir a ela uma metodologia de pesquisa JEV,
uma amostragem representativa ou capacidade de produzir estatísticas oficiais.

## Alternativas consideradas

| Alternativa | Benefícios | Limitações | Encaminhamento proposto |
| --- | --- | --- | --- |
| Manter o pipeline Gemini atual | Menor complexidade; comportamento existente testado | Não atende a escolha de modelos locais | Manter como baseline durante a evolução |
| Adaptadores local/cloud sob o mesmo contrato | Atende ao requisito da #10 sem acoplar o mapa ao runtime | Exige normalizar capacidades, erros e conclusão da geração | Implementar na #10 |
| Criar um serviço ou motor independente denominado JEV | Poderia encapsular regras próprias, se elas existirem | Responsabilidades e necessidade ainda não definidas | Não justificar essa extração apenas pelo nome |
| Adicionar fontes verificáveis e recuperação de documentos | Poderia sustentar rastreabilidade factual | Requer fontes, contratos, critérios e avaliação adicionais | Avaliar somente após definir objetivos de domínio |

## Recomendação provisória

Preservar a separação interface → geração → validação → visualização e o contrato
de dados existente. Implementar a variação de provedor na camada de serviços,
conforme a #10, sem criar um componente JEV independente sem responsabilidades
definidas. Registrar limites qualitativos dos scores e separar explicitamente
validação estrutural de comprovação factual.

Esta recomendação é proporcional ao código e aos requisitos conhecidos; não é
uma decisão aceita sobre a identidade da JEV. Após a definição do responsável:

- Se JEV for o nome do produto, registrar isso e confirmar a manutenção do pipeline.
- Se for uma metodologia, mapear suas etapas/regras para o pipeline e identificar lacunas.
- Se for um mecanismo específico, documentar suas referências, entradas, saídas e critérios
  de sucesso antes de decidir sua integração ou extrair um novo componente.

## Plano de avaliação

Reutilizar os cenários e o protocolo da #4, descritos em
[PROMPT_DESIGN.md](../PROMPT_DESIGN.md), para evitar uma segunda avaliação paralela.
O significado de JEV determinará se é necessário acrescentar cenários de domínio.

| Dimensão | Como avaliar | Critério proposto |
| --- | --- | --- |
| Contrato | Fixtures inválidas/válidas e suíte offline | Todos os casos esperados passam; respostas inválidas não chegam ao mapa |
| Estado e regressões | Reruns, erros, demo, resposta vazia | Nenhuma chamada extra por rerun; resultado anterior preservado em falhas |
| Semântica | Veículos elétricos com métrica explícita; contextos equivalentes; tema fictício | Revisão humana identifica critério coerente, ausência de contraste inventado e justificativas sustentáveis |
| Fatos | Revisar justificativas com fontes adequadas, data e revisor registrados | Registrar cada afirmação como sustentada, contradita ou inconclusiva; não declarar qualidade com pendências omitidas |
| Comparação | Mesmos casos/modelo, baseline e refinado, 3 repetições alternadas | Comparar evidências por caso; dispersão dos scores não define vencedor |
| Latência | Tempo completo por caso e variante na avaliação real | Registrar medianas e falhas; limites aceitáveis do produto ainda precisam ser definidos |
| Contribuição específica da JEV | Depende de definir o que ela adiciona ao pipeline | Antes de implementar, definir baseline, cenários e limiares próprios; não atribuir ganhos só ao nome |

Não há baseline factual de referência nem limiar de qualidade confirmado. As
categorias acima permitem uma avaliação auditável, mas não substituem a definição
dos critérios de sucesso específicos da JEV. A #8 pode ser encerrada com um plano
acordado; a execução empírica e seus resultados permanecem na #4.

### Evidências disponíveis nesta revisão

- `.venv/bin/python -m unittest discover -s tests -q`: 29 testes aprovados.
- `.venv/bin/python evaluate_prompts.py --output artifacts/issue-8-offline-evaluation.json`:
  quatro fixtures com os resultados esperados; nenhuma chamada à API.
- [Relatório offline versionado](../evaluations/offline.json): evidência histórica
  do contrato com dados fictícios; não mede factualidade ou latência da LLM.
- Não foi executada geração real, nem avaliação factual de novas respostas.

## Próximas ações e dependências

1. **Prioridade imediata — #8:** confirmar significado, finalidade e casos de uso
   da JEV; preencher a definição, revisar esta recomendação e registrar a decisão
   final, seus contratos e critérios de sucesso. Depende do responsável pelo produto.
2. **Evolução funcional — #10:** implementar runtime local, adaptadores e seleção
   de provedor/modelo, preservando contrato e identificação do resultado. A issue
   já existe; esta análise não cria uma duplicata.
3. **Avaliação empírica — #4:** executar o protocolo real e revisar as justificativas.
   Qualquer afirmação de melhoria factual ou de velocidade depende dessa evidência.
4. **Após a definição — #8:** derivar novas issues apenas para lacunas de domínio
   justificadas. Rastreabilidade completa de exportações e integração de fontes
   são lacunas candidatas, não entregas aprovadas nesta revisão.

## Condição para encerramento da #8

Confirmar a definição de JEV, concluir esta ADR, registrar o plano de avaliação
pertinente e disponibilizar a documentação revisada no repositório. Enquanto a
definição estiver pendente, a análise do código pode avançar, mas o primeiro
critério de aceite da issue não está atendido e ela deve permanecer aberta.
