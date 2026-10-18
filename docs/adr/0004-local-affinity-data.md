# ADR 0004 — snapshots locais para dados de afinidade

- Data: 05/10/2026.
- Estado: proposta inicial; validar no piloto da #13.
- Issue: [#13](https://github.com/felpzw/jev-global-heatmap/issues/13).
- Depende de: [ADR 0003](0003-affinity-ranking.md) e contratos da #14.
- Evidências e comparação: [pesquisa de dados](../DATA_RESEARCH.md).

## Contexto

O ranking precisa de atributos verificáveis, com ausência explícita e versões
capazes de reproduzir o resultado. O primeiro catálogo cobre poucos critérios
de praia e idioma para 195 Estados. Ainda não há dataset de afinidade, medição
de volume ou necessidade demonstrada de banco servidor.

## Decisão proposta

Adotar JSON para catálogo, fontes e manifesto; JSONL para evidências e valores
resolvidos. Arquivos pequenos e licenciados compõem snapshots imutáveis no Git.
Carregar um índice Python por país/atributo no ranking, usando versão explícita.
O formato e a validação serão alinhados aos contratos da #14 antes da implementação.

Separar aquisição e manutenção da execução do ranking. Conectores candidatos
obtêm dados estruturados ou arquivos específicos em jobs limitados, preservando
bruto/revisão, hashes e transformações. Publicar somente após validar e revisar
as diferenças; `local_only` não acessa rede. Nenhum conector é implementado ou
declarado aprovado por esta proposta.

Investigar Wikidata para idiomas oficiais, com revisão de fontes oficiais;
Natural Earth e curadoria para litoral. Proficiência e qualidade de praia não
são habilitadas até confirmar definição, evidência e reuso adequados.

Preservar observações e conflitos separados do valor selecionado. Ausência,
conflito ou expiração impedem o uso conforme a política de cobertura vigente;
um false demonstrado continua sendo valor válido. Registrar licenças por origem.

## Alternativas e consequências

- CSV permanece opção de exportação, com convenções de tipos e ausência.
- SQLite oferece SQL/transações em arquivo local; pode ser adotado se histórico
  e consultas justificarem seu custo. Uma derivação SQLite deve ser reconstruível
  e não se tornar uma segunda fonte editável dos mesmos fatos.
- Parquet/DuckDB são candidatos para séries ou volume analítico maior.
- Banco servidor fica adiado até existir necessidade operacional concreta.
- JSON/JSONL facilita revisão no Git, mas exige validação de relações e publicação
  do snapshot completo. Não oferece transação de múltiplos arquivos por si só.
- A retenção dos brutos necessários é parte da reprodução; guardar só uma URL
  não garante reconstrução. Artefatos grandes precisam de arquivo persistente.

## Condições para confirmar ou revisar

Confirmar após obter e reconstruir offline a amostra, medir cobertura admissível
por critério e alinhar o contrato com #14. Medir custo de leitura e manutenção;
comparar formatos no mesmo workload se houver necessidade concreta. Mudanças
de escala, histórico ou concorrência podem levar a outra decisão.

Esta ADR não declara a #13 concluída nem altera o MVP executável.
