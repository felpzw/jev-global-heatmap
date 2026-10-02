# Arquitetura e Fluxo de Dados

## 1. Fluxo Principal
1. **Input UI:** Usuário insere o contexto/tema no `src/app.py`.
2. **LLM Service:** `src/services/llm_client.py` envia o prompt + input para a IA solicitando uma saída JSON estruturada.
3. **Data Parsing:** A resposta é validada via Pydantic para garantir que contenha a chave do país e o score numérico.
4. **Map Rendering:** `src/components/map_renderer.py` consome o JSON validado e monta uma figura `plotly.graph_objects.Choropleth`, sem um DataFrame intermediário.

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
Antes de validar o JSON, o serviço exige uma resposta concluída (`finish_reason=STOP`).
Gerações interrompidas, bloqueadas ou sem candidatos não substituem o resultado
anterior, mesmo que o trecho retornado seja JSON válido.

## 3. Interface e avaliação

- A UI só chama o serviço no envio do formulário; entradas vazias são barradas.
- `session_state.mapping` guarda resposta, contexto e origem (`gemini`/`demo`).
  Reruns não disparam consultas. Falhas mantêm o resultado anterior identificado.
- `plot_heatmap` valida dados, retorna `Figure` e não depende de Streamlit.
- A figura é construída ao salvar um resultado e reutilizada na própria sessão,
  sem cache global de contextos. Uma revisão derivada dos dados permite preservar
  o enquadramento em reruns e reiniciá-lo quando o resultado muda.
- O mapa usa escala fixa 0–100 e cinza para ausência de dados. A geografia de
  base é carregada pelo navegador a partir do CDN do Plotly.
- `src/services/prompts.py` é a fonte executável dos prompts. O refinado pede
  uma amostra de até 40 países para reduzir geração; isso é uma orientação,
  não uma garantia de cobertura mundial nem uma otimização medida.
- `evaluate_prompts.py` separa fixtures offline de comparação real, incluindo
  tempos, distribuição e respostas para revisão humana. Não há busca na web
  nem validação factual automatizada neste MVP.
