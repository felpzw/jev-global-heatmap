# Dados, proveniência e reprodução

Release de demonstração: `factbook-archive-v1`. Registro: 193 membros ONU + Santa
Sé/VAT e Palestina/PSE; sem dependências, Kosovo ou Taiwan no conjunto pontuado.
As geometrias do Plotly podem representar outras unidades; não alteram o registro.

## Fontes e licenças

| Artefato | Origem e reuso | Transformação |
| --- | --- | --- |
| `sources/factbook_extract.json` | Fatos do governo dos EUA em domínio público; espelho [factbook.json](https://github.com/factbook/factbook.json), revisão `144d6977b2b01ac1cbd220de754c0a005616760b`; [licença CC0 do espelho](https://github.com/factbook/factbook.json/blob/144d6977b2b01ac1cbd220de754c0a005616760b/LICENSE.md) | Somente campos Coastline, Languages e identificadores nacionais; hashes dos perfis originais e dos arquivos locais |
| `sources/factbook_routes.json` | Roteamento explícito entre IDs internos e perfis públicos | Código ISO alpha-2 conferido contra Internet country code de cada perfil; GBR permite `.uk`; PSE agrega Gaza e Cisjordânia |
| `country_registry.json` | Códigos, nomes e tradução de [pycountry](https://github.com/pycountry/pycountry), baseado em Debian iso-codes, LGPL 2.1 ou posterior | Recorte explícito dos 195 IDs; M49 como string; [licença](licenses/pycountry-LGPL-2.1.txt) e [copyright](licenses/pycountry-COPYRIGHT.txt) preservados |
| `affinity_demo.json` | Fixture sintética própria, CC0-1.0 | Oito países com valores fictícios; demais posições ausentes |
| `criteria_catalog.json` | Definições e regras próprias | Dois booleanos, comparação `eq`, normalização 0/1 e ausência explícita |

O escopo do registro segue [membros ONU](https://www.un.org/en/about-us/member-states)
e [observadores](https://research.un.org/en/unmembers/observers). Essas páginas
são referências de escopo; seus textos/tabelas não foram redistribuídos. Nenhuma
tabela completa de códigos de terceiros com licença incerta acompanha o projeto.

A CIA anunciou o [encerramento do Factbook em 04/02/2026](https://www.cia.gov/stories/story/spotlighting-the-world-factbook-as-we-bid-a-fond-farewell/).
Coleta e revisão do espelho não equivalem à data de publicação ou à vigência do
fato. `published_at` é null porque esses campos não informam uma data única.
Datas citadas dentro dos textos brutos são preservadas. A curadoria é derivação
automática conservadora, sem auditoria humana completa das afirmações nacionais.

## Regras da release

- Litoral: `0 km`/`landlocked` → false; número positivo de km → true. O próprio
  arquivo explicita Cáspio/Aral como landlocked para KAZ/AZE/TKM. PSE usa `any`
  de Gaza/Cisjordânia. Não agrega territórios dependentes à metrópole.
- Idioma: marcador explícito `English (official)` (incluindo `English only`) ou
  frases explícitas sobre inglês oficial nacional/subsidiário → true. Lista
  oficial sem menção ao inglês → false. Texto inconclusivo, inglês sem status
  explícito ou divergência entre perfis → missing. Amostras de tradução em inglês
  dentro do perfil não contam como idioma oficial. Idiomas de facto ficam ausentes.
- `missing`, `conflicting`, `expired` e `not_applicable` nunca pontuam. Na primeira
  release há apenas observed/missing; os contratos reservam os demais estados.
- Com dois critérios ativos, cobertura conjunta observada: 133/195. Somente
  litoral: 195/195. São 151 true/44 false para litoral e 47 true/86 false para
  inglês oficial. Cobertura mede extração admissível, não precisão ou vigência.
- Snapshot histórico permanece utilizável como demonstração com aviso; expiração
  não é inferida da coleta. Uso factual atual requer revisão e uma nova release.

## Reconstruir e atualizar

```sh
# Sem rede; reconstrói byte a byte e verifica a release existente
python -m scripts.verify_dataset
# Deriva novamente os artefatos locais; usar durante preparação de uma nova release
python -m scripts.build_dataset
# Aquisição explícita opcional: 196 perfis, 4 conexões, 30 s/arquivo, até 2 MB/arquivo
python -m scripts.acquire_factbook
```

O ranking nunca executa aquisição. Os extratos mantidos no Git permitem reconstruir
evidências, cobertura e manifesto sem os perfis completos. Para auditar a extração,
as URLs fixadas e hashes permitem baixar cada perfil original e conferir os campos.
O manifesto também identifica o hash do código de transformação. Nenhuma revisão
do snapshot é trocada durante uma execução.

Revisar mensalmente correções e fontes substitutas atuais; o arquivo encerrado
não receberá atualização oficial. Mudanças de valores, critérios ou fontes geram
`v2`, novos hashes e relatório de diferenças; não alterar a release publicada.
Preservar snapshots e extratos pequenos no Git; não há necessidade de SQLite,
PostgreSQL, DuckDB ou scheduler para este volume. Rollback seleciona uma versão
anterior com as mesmas regras. Checkpoints de sessão ficam em `artifacts/`, fora
do Git; podem ser removidos com o aplicativo parado se a retomada não for desejada.
