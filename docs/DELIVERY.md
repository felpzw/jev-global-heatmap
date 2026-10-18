# Entrega e avaliação das issues — 18/10/2026

Destino da integração: `develop`. A `main` permanece a versão anterior até uma
promoção própria. Nenhum stash foi encontrado no início; nenhum foi criado ou
descartado. A pesquisa de dados que já estava no diretório foi preservada no
commit `62bf4db`, antes da implementação.

| Issue | Resultado técnico | Evidências / limite |
| --- | --- | --- |
| #13 · Dados | Implementada para o catálogo inicial | Snapshot com 390 posições, 195/195 litoral e 133/195 idioma; extratos, hashes, cobertura e reconstrução offline; fontes históricas, sem auditoria factual completa |
| #14 · Fundação | Implementada | Registro ONU 195; contratos estritos; score/estado/seleção/explicação independentes; finitude, duplicatas e round-trip testados |
| #15 · Motor | Implementada | Parser conservador, revisão obrigatória, filtros e score ponderado, desempate ISO, seleção 20/10, adaptador restrito e fallback; cache/checkpoints/cancelamento cooperativo |
| #16 · Interface | Implementada | Mapa, estados, ranking, critérios, fontes, busca por 195, fixture fictícia, JSON e regressões de sessão; base cartográfica usa CDN |
| #17 · Avaliação | Parte offline implementada; aceite externo pendente | Protocolo, casos tune/test, baseline simples, métricas e latências; comparação Gemini real e revisão humana no repasse |

## Verificações

- 61 testes offline aprovados, incluindo MVP preservado, contratos JEV, motor, mapa, interface,
  métricas e integração do SDK real sobre HTTP simulado.
- `python -m scripts.verify_dataset`: reconstrução idêntica dos artefatos e
  verificação de integridade, sem rede.
- `python evaluate_affinity.py`: metas funcionais aprovadas nas fixtures anotadas.
- `python -m pip check`: dependências consistentes.
- Workflow GitHub Actions: instalação, integridade, testes e avaliação sem chaves.
- Execução local no Safari: revisão/confirmacão, resultado, mapa e ranking visíveis.

No teste sintético: recall de candidatos 1,0; precision@3 0,722 (inclui caso sem
resultados no agregado); NDCG@3 1,0 nos casos com relevância definida. Zero requisito
violado e zero falso descarte anotado. Paridade com baseline simples nesses casos;
nenhuma superioridade do ranker foi demonstrada. Latência e ambiente estão no JSON,
sem generalização para produção. O arquivo real mede cobertura, sem notas de
relevância humana ou verificação de vigência nacional.

## Organização do histórico

1. Preservar pesquisa inicial em commit documental próprio.
2. Implementar fundação e dados versionados.
3. Implementar motor, seleção e resiliência com testes.
4. Integrar interface e manter o MVP em `src/legacy_app.py`.
5. Publicar avaliação, CI, documentação, repasse e kit de portfólio.
6. Abrir PR para `develop`, conferir verificações e integrar por merge commit,
   preservando os commits temáticos e as branches existentes.

A situação efetiva do merge e das verificações remotas consta na PR. Os commits
locais não reescrevem história publicada. Credenciais, checkpoints e relatórios
de sessão permanecem fora do Git.

Pendência manual necessária: [HANDOFF.md](HANDOFF.md). Material de publicação:
[PORTFOLIO.md](PORTFOLIO.md). O encerramento da #17 depende das evidências reais
e da revisão humana descritas no repasse, não apenas da passagem dos testes.
