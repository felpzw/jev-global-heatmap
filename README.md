# JEV Global Heatmap

Projeto de heatmap de **ranking de afinidade com o pedido**. A arquitetura-alvo
usa a JEV para interpretar critérios suportados, filtrar países e calcular scores
0–100 com dados e regras; Gemini justifica somente os melhores selecionados.

## Evolução: ranking de afinidade com JEV

O usuário confirma requisitos obrigatórios, preferências e pesos. A JEV usa um
catálogo pequeno e dataset local versionado; dados insuficientes e exclusões
ficam explícitos. O score representa afinidade, sem interpretação probabilística.
A LLM recebe somente países selecionados e evidências, sem alterar scores ou ordem.
Sem chave ou em `local_only`, a explicação usa templates e o ranking funciona.

**Essa evolução ainda não está implementada.** O executável disponível continua
sendo o MVP Gemini, que recebe texto e gera países/scores qualitativos diretamente.
As instruções abaixo pertencem a esse MVP.

- [Arquitetura](ARCHITECTURE.md) e [ADR 0003](docs/adr/0003-affinity-ranking.md).
- [Contratos e desenho](docs/JEV_DESIGN.md), [plano e issues](docs/JEV_IMPLEMENTATION_PLAN.md).
- [MVP executável](docs/MVP_LEGACY.md) e [propostas históricas](docs/legacy/README.md).

## Stack do MVP executável
* **UI & App:** Streamlit
* **Visualização:** Plotly Graph Objects
* **IA & Dados:** Pydantic (Structured Outputs) + LLM API

## Como rodar o MVP localmente

Requer Python 3.12+ (validado com Python 3.14). Na raiz do projeto:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Preencha `GEMINI_API_KEY` no `.env`. `GOOGLE_API_KEY` também é aceito como fallback
quando a primeira estiver ausente, vazia ou contiver apenas espaços.
`GEMINI_MODEL` permite escolher um modelo com Structured Outputs; o padrão é
`gemini-3.5-flash-lite`. Nunca versione o `.env`.

```sh
python -m streamlit run src/app.py
```

Sem chave, use **Carregar demonstração** na barra lateral. Os dados são fictícios.
Com a chave configurada, descreva um tema e clique em **Gerar Mapeamento**.
O mapa, a tabela de justificativas e o download JSON permanecem disponíveis
entre reruns da mesma sessão. Uma falha preserva o resultado anterior, identificado
pelo contexto original; recarregar a página ou abrir outra sessão pode limpar o estado.
Respostas interrompidas pelo limite de geração ou bloqueadas pelo provedor são
recusadas, mesmo quando contêm JSON válido.

Os scores são estimativas qualitativas produzidas pelo modelo, sem pesquisa em
tempo real. Países não retornados ficam cinza, sem atribuição artificial de zero.
O mapa base do Plotly requer acesso do navegador ao CDN de geometrias.
O mapa tem fundo transparente, legenda horizontal e controles de zoom na barra
do gráfico; a rolagem da página não aciona zoom. A figura é reutilizada em reruns.
Veja o [redesign e roteiro de testes manuais](docs/MAP_REDESIGN.md).

## Validação do pipeline do MVP

```sh
# Testes offline, sem credenciais ou chamadas à API
python -m unittest discover -s tests -v
# Smoke test real; utiliza a API configurada
python test_llm.py "Adoção de carros elétricos"
```

## Avaliação de prompts do MVP

```sh
# Fixtures fictícias, sem API: valida contrato e calcula distribuição de scores
python evaluate_prompts.py
# Comparação real baseline/refinado: 3 cenários × 2 prompts × 3 repetições = 18 chamadas
python evaluate_prompts.py --live --repeats 3
```

O relatório padrão fica em `artifacts/prompt_evaluation.json` (ignorado pelo Git).
A execução real pode gerar custos. As justificativas precisam de revisão manual;
validez do JSON e dos códigos ISO não prova precisão factual dos scores.
Veja [o protocolo e as limitações](docs/PROMPT_DESIGN.md),
[o relatório offline](docs/evaluations/offline.json) e
[a sequência de branches e merges](docs/IMPLEMENTATION.md).
