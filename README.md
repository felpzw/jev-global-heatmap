# JEV Global Heatmap

Protótipo rápido de pesquisa de amostragem global. O sistema recebe um input textual (tema de pesquisa), processa o contexto via IA e gera um mapa de calor coroplético mundial indicando a relevância/intensidade do tema por país.

## Evolução: JEV sem LLM

A nova arquitetura usa a JEV para coordenar fontes/datasets, normalização e
estimativas estatísticas por evento e prazo, sem chamadas de LLM. O usuário
escolhe um evento suportado por domínio; haverá um registro dos 195 Estados e
status explícitos quando os dados forem insuficientes. Fonte, banco e estimador
iniciais ainda serão selecionados.

**Essa evolução ainda não está implementada.** O código atual continua usando
Gemini e scores qualitativos. As instruções de execução abaixo são do MVP.

- [Nova arquitetura](ARCHITECTURE.md) e [ADR 0002](docs/adr/0002-jev-without-llm.md).
- [Contratos e desenho](docs/JEV_DESIGN.md), [plano e issues](docs/JEV_IMPLEMENTATION_PLAN.md).
- [MVP executável](docs/MVP_LEGACY.md) e [histórico com LLM](docs/legacy/README.md).

## Stack
* **UI & App:** Streamlit
* **Visualização:** Plotly Graph Objects
* **IA & Dados:** Pydantic (Structured Outputs) + LLM API

## Como rodar localmente

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

## Validação do pipeline

```sh
# Testes offline, sem credenciais ou chamadas à API
python -m unittest discover -s tests -v
# Smoke test real; utiliza a API configurada
python test_llm.py "Adoção de carros elétricos"
```

## Avaliação de prompts

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
