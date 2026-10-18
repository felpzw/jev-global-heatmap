# JEV Global Heatmap

Uma ideia se transforma em critérios revisáveis e em um **mapa mundial de
afinidade**. A JEV filtra e calcula o ranking com dados locais e regras; o Gemini,
quando habilitado, explica somente os selecionados. O projeto demonstra busca
conceitual explicável com um catálogo inicial de litoral marítimo e inglês oficial
nacional. Não interpreta qualquer assunto e não usa embeddings.

## Experimente

Python 3.12+; validado localmente com Python 3.14. Na raiz:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run src/app.py
```

**Nenhuma chave é necessária.** Escolha um exemplo, revise requisitos,
preferências e pesos, confirme e clique em **Calcular afinidade global**.

| Pedido | O que demonstra |
| --- | --- |
| Prefiro litoral e inglês oficial | Combinação de conceitos e pesos |
| Exijo litoral e prefiro inglês oficial | Filtro obrigatório antes do ranking |
| Prefiro países sem litoral | Negação explícita |
| Quero praia e inglês | Esclarecimento: praia ≠ litoral; proficiência ≠ idioma oficial |

O mapa colore todos os países com score, destaca os candidatos e distingue
exclusões e lacunas. Tabela pesquisável, fatores, evidências e JSON cobrem os
195 Estados do registro, inclusive microestados sem geometria representativa.
Scores de 0 a 100 representam afinidade, sem interpretação probabilística.

## Dados e explicações

O snapshot histórico do Factbook possui 195/195 valores de litoral e 133/195 de
inglês oficial. Os 62 casos inconclusivos de idioma permanecem ausentes; não
viram zero. São 390 posições país/critério com proveniência, hashes e transformação
reproduzível. O Factbook foi encerrado em 2026; o arquivo não garante vigência
atual. Litoral não mede qualidade de praia e idioma oficial não mede proficiência.
Veja [fontes, licenças e políticas](data/SOURCES.md).

A opção **Demonstração fictícia** usa uma fixture separada, sempre identificada.
O modo `local_only` não usa rede no motor nem nas explicações. O navegador
precisa acessar o CDN de geometrias do Plotly para desenhar o mapa base.

Para explicações Gemini, copie `.env.example` para `.env`, configure
`GEMINI_API_KEY` (ou `GOOGLE_API_KEY`) e `GEMINI_MODEL`, e desative **Somente motor
local**. O modelo padrão continua configurável em `.env.example`; o ensaio real
precisa verificar sua disponibilidade na conta. Máximo de 20 candidatos, 10
justificativas, uma chamada, 4096 tokens de saída e 30 s. Falhas usam templates
e preservam scores. Cancelamento é cooperativo; a chamada já enviada pode terminar
no provedor. Reruns e cache são isolados por sessão. Nunca versione credenciais.

## Validação e avaliação

```sh
python -m unittest discover -s tests -v
python -m scripts.verify_dataset
python -m pip check
python evaluate_affinity.py --output artifacts/affinity-evaluation.json
# Opcional: 6 consultas × 2 variantes × 3 repetições; pode gerar cobrança
python evaluate_affinity.py --live --repeats 3 --output artifacts/affinity-live.json
```

[Protocolo](docs/EVALUATION_PROTOCOL.md) e [relatório offline](docs/evaluations/affinity_offline.json):
metas funcionais aprovadas; recall de candidatos 1,0, precision@3 0,722 e NDCG@3
1,0 no conjunto sintético de teste. Esses números não comprovam relevância em
pedidos reais, qualidade factual ou economia de tokens/custo. Revisão humana e
comparação Gemini real estão no [repasse manual](docs/HANDOFF.md).

## Projeto e portfólio

- [Arquitetura](ARCHITECTURE.md), [contratos](docs/JEV_DESIGN.md) e [ADR de dados](docs/adr/0004-local-affinity-data.md).
- [Situação das issues e evidências](docs/DELIVERY.md), [plano](docs/JEV_IMPLEMENTATION_PLAN.md) e [como estender a JEV](docs/EXTENDING_JEV.md).
- [Kit para LinkedIn e portfólio](docs/PORTFOLIO.md): narrativa, roteiro de demonstração, números verificáveis e limites.
- [MVP Gemini preservado](docs/MVP_LEGACY.md): `python -m streamlit run src/legacy_app.py`.
- [Pesquisa original de dados](docs/DATA_RESEARCH.md) e [propostas anteriores](docs/legacy/README.md).
