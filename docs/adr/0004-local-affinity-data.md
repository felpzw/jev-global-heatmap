# ADR 0004 — snapshots locais para dados de afinidade

- Data da proposta: 05/10/2026; decisão confirmada em 18/10/2026.
- Estado: aceita para a release de demonstração.
- Issue: [#13](https://github.com/felpzw/jev-global-heatmap/issues/13).
- Depende de [ADR 0003](0003-affinity-ranking.md) e contratos da #14.
- Investigação original preservada em [DATA_RESEARCH.md](../DATA_RESEARCH.md).

## Contexto

O ranking precisa de atributos rastreáveis, com ausência explícita e versões
que reproduzam o resultado. O catálogo inicial contém dois booleanos para
195 Estados. Não foi demonstrada necessidade de banco servidor ou consulta
online durante o ranking.

## Decisão

JSON para catálogo, registro, extratos e manifesto; JSONL para evidências.
Arquivos pequenos e permitidos ficam no Git como snapshots completos e
imutáveis após publicação. O motor valida os hashes e carrega um índice por
país/atributo. A aquisição é um comando explícito separado da execução.

A release `factbook-archive-v1` usa campos do arquivo público Factbook na revisão
`144d6977b2b01ac1cbd220de754c0a005616760b`, com extratos preservados, URLs fixadas,
hashes dos perfis e código de transformação identificado. A tabela de códigos
inicialmente investigada não é redistribuída; os perfis são validados pelo
próprio campo Internet country code. Gaza e Cisjordânia são agregadas em PSE.

O Factbook foi encerrado em 2026. A release é histórica, sem garantia de vigência
atual. Idioma de facto, status inconclusivo e ausência permanecem missing;
proficiência e qualidade de praia não foram habilitadas. Fontes, licenças,
regras e política territorial estão em [SOURCES.md](../../data/SOURCES.md).

## Evidências do piloto

- 390 posições país/critério: litoral 195/195 e inglês oficial 133/195.
- 62 lacunas de idioma explícitas, sem inferência por LLM ou imputação.
- Reconstrução offline byte a byte aprovada por `scripts.verify_dataset`.
- Nenhuma consulta SQL ou volume observado justificou acrescentar banco.
- Cobertura de extração não comprova precisão ou vigência dos fatos.

## Alternativas e consequências

CSV é exportação; SQLite pode ser uma derivação para histórico/consultas se
necessário. Parquet/DuckDB ficam para volume analítico maior. Banco servidor
permanece adiado. JSON/JSONL facilita revisão, mas integridade relacional e
publicação do conjunto dependem do validador e do manifesto.

Preservar extratos necessários para reprodução. Mudanças de fonte, valor,
catálogo ou transformação exigem nova release e hashes; rollback usa a versão
anterior e invalida o cache por identidade. Expansões de escala, concorrência,
critérios ou exigência de dados atuais podem revisar esta decisão.
