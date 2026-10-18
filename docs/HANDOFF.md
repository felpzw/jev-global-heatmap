# Repasse manual — 18/10/2026

O fluxo local está implementado. A pendência de aceite da #17 exige credenciais
do provedor e julgamento humano, ausentes neste ambiente. O projeto não precisa
de uma implementação manual adicional para rodar a demonstração sem API.

## Ensaio real da #17

1. Criar `.env` a partir de `.env.example` e configurar a própria chave Gemini e
   um modelo com Structured Outputs disponível na conta. Não publicar o arquivo.
2. Ler [o protocolo](EVALUATION_PROTOCOL.md) e executar:

   ```sh
   python evaluate_affinity.py --live --repeats 3 --output artifacts/affinity-live.json
   ```

   São até 36 chamadas (6 consultas × 2 variantes × 3 repetições), com cobrança
   conforme a conta; o caso vazio pode evitar a chamada JEV. Não executar em loop.
3. Conferir status por chamada, truncamentos, tokens disponíveis e p50/p95 por
   variante. Registrar a tarifa consultada, sua data e modelo antes de calcular
   custos. Custo null significa não medido; falha não representa economia.
4. Revisar cada afirmação das justificativas e IDs de evidência. Registrar revisor,
   data, sustentada/não sustentada/inconclusiva e razão. Conferir ordem, filtros
   e ausência de fatos que não estejam no payload.
5. Anotar um conjunto independente de consultas reais com julgamentos de relevância
   antes de avaliar qualidade externa. Conferir especialmente idioma oficial vs.
   de facto, status regional, vigência e agregação nacional. A release histórica
   não substitui essa revisão.
6. Salvar o relatório revisado em `docs/evaluations/`, atualizar os itens restantes
   da #17 e fechar a issue somente com essas evidências. Não há alegação atual de
   economia, precisão universal ou superioridade sobre baselines.

## Demonstração e publicação

- Rodar `python -m streamlit run src/app.py`, confirmar os critérios e verificar
  hover/zoom, busca por VAT/PSE, JSON e leitura em celular. O mapa usa CDN: reservar
  conexão ao gravar. Microestados permanecem pesquisáveis na tabela.
- Gravar o roteiro de [PORTFOLIO.md](PORTFOLIO.md) e revisar o texto antes de postar.
  Nenhuma publicação no LinkedIn foi feita automaticamente.
- Hospedagem é opcional e não foi provisionada: em um serviço compatível com
  Streamlit, usar `src/app.py`, Python 3.12+ e `requirements.txt`; guardar a chave
  no gerenciador de segredos do host, habilitar acesso ao CDN e validar quotas.
  Sem chave, a demonstração local continua funcional.
- A integração desta entrega tem destino `develop`. A promoção para `main` e uma
  URL pública podem ser feitas após escolher a hospedagem e concluir a revisão.
