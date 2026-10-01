# Arquitetura e Fluxo de Dados

## 1. Fluxo Principal
1. **Input UI:** Usuário insere o contexto/tema no `src/app.py`.
2. **LLM Service:** `src/services/llm_client.py` envia o prompt + input para a IA solicitando uma saída JSON estruturada.
3. **Data Parsing:** A resposta é validada via Pydantic para garantir que contenha a chave do país e o score numérico.
4. **Map Rendering:** `src/components/map_renderer.py` consome o JSON validado e plota o mapa via `plotly.express.choropleth`.

## 2. Contrato de Dados (Pydantic Schema)
O modelo DEVE retornar um objeto `HeatmapResponse` com a chave `countries`,
contendo uma lista de objetos `CountryHeatmap` neste formato:
- `iso_alpha_3` (string): Código de 3 letras do país (Padrão ISO 3166-1 alpha-3. Ex: "BRA", "USA"). Essencial para o Plotly renderizar.
- `heat_score` (float): Valor numérico de 0.0 a 100.0 representando a intensidade.
- `context_summary` (string): Breve justificativa de 1 frase do score atribuído àquele país (usado no tooltip ao passar o mouse no mapa).

O schema rejeita campos extras, países duplicados, códigos inexistentes no catálogo
`pycountry`, valores não numéricos, infinitos/NaN e justificativas vazias ou maiores
que 300 caracteres. Uma lista vazia representa contexto insuficiente; países ausentes
não recebem score zero. O limite é de 249 entradas.

O serviço usa Gemini Structured Outputs e revalida o JSON localmente antes de
retorná-lo. O timeout HTTP é de 60 segundos, sem repetição automática de chamadas.
Erros do provedor são convertidos em mensagens sem credenciais ou respostas brutas.
