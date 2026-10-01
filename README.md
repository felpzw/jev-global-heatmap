# JEV Global Heatmap

Protótipo rápido de pesquisa de amostragem global. O sistema recebe um input textual (tema de pesquisa), processa o contexto via IA e gera um mapa de calor coroplético mundial indicando a relevância/intensidade do tema por país.

## Stack
* **UI & App:** Streamlit
* **Visualização:** Plotly Express
* **IA & Dados:** Pydantic (Structured Outputs) + LLM API

## Como rodar localmente

1. Clone o repositório e ative o ambiente virtual:
   `source venv/bin/activate`
2. Instale as dependências:
   `pip install -r requirements.txt`
3. Configure as credenciais copiando o `.env.example` para `.env` e inserindo sua API Key.
4. Inicie o app:
   `streamlit run src/app.py`
