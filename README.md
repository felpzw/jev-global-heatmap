# JEV Global Heatmap

Protótipo rápido de pesquisa de amostragem global. O sistema recebe um input textual (tema de pesquisa), processa o contexto via IA e gera um mapa de calor coroplético mundial indicando a relevância/intensidade do tema por país.

## Stack
* **UI & App:** Streamlit
* **Visualização:** Plotly Express
* **IA & Dados:** Pydantic (Structured Outputs) + LLM API

## Como rodar localmente

Requer Python 3.12+ (validado com Python 3.14). Na raiz do projeto:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Preencha `GEMINI_API_KEY` no `.env`. `GOOGLE_API_KEY` também é aceito como fallback.
`GEMINI_MODEL` permite escolher um modelo com Structured Outputs; o padrão é
`gemini-3.5-flash-lite`. Nunca versione o `.env`.

```sh
python -m streamlit run src/app.py
```

## Validação do pipeline

```sh
# Testes offline, sem credenciais ou chamadas à API
python -m unittest discover -s tests -v
# Smoke test real; utiliza a API configurada
python test_llm.py "Adoção de carros elétricos"
```
