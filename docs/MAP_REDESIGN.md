# Redesign do mapa — issue #7

Branch: `feat/issue-7-map-redesign`, baseada na `develop` (`ab78177`).
O merge na `develop` aguarda os testes manuais do responsável. Nenhum review
formal foi solicitado ou enviado e o merge automático não foi habilitado.

## Proposta

- Fundo transparente na figura, plot e área geográfica; oceano sem preenchimento.
- Mantida a projeção Natural Earth, a escala YlOrRd de 0–100 e o cinza para ausência
  de dados. Zero continua sendo uma observação válida, com cor própria da escala.
- Legenda horizontal, margens laterais menores, altura de 460 px e largura fluida.
- Fronteiras neutras e tooltip com fundo escuro, texto branco e quebra de linhas.
  Justificativas continuam escapadas antes da inserção no HTML do tooltip.
- Sem animação automática; duração de transição zero, inclusive para quem prefere
  movimento reduzido. Zoom pela barra do gráfico, sem capturar rolagem da página.
- Construção direta com Graph Objects, eliminando DataFrame e processamento do
  Plotly Express. Figura reutilizada apenas na sessão do usuário.
- `uirevision` derivado dos dados permanece estável em reruns. Novos dados mudam
  a revisão para reiniciar o enquadramento. A persistência efetiva no navegador
  precisa ser confirmada no roteiro abaixo; recarregar a página pode limpar a sessão.

Referências: [Plotly geo](https://plotly.com/python/reference/layout/geo/),
[uirevision](https://plotly.com/python/reference/layout/#layout-uirevision) e
[integração Streamlit](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart).

## Medições reproduzíveis

```sh
.venv/bin/python benchmark_map.py --baseline-ref ab78177
.venv/bin/python -m http.server 8502 --bind localhost --directory artifacts/redesign
```

Abra `http://localhost:8502/benchmark.html`. A página compara as figuras em
largura fluida ou 320 px e fundos claro/escuro; o botão de medição registra
`Plotly.newPlot` e atualização de scores com `Plotly.react`, incluindo dois frames
de pintura, 1 aquecimento e 10 repetições alternadas por caso. Copie o JSON exibido
para registrar navegador, viewport e resultados. São dados fictícios, sem LLM.
A página isolada não substitui a validação dos temas e reruns no Streamlit.

O script também grava `artifacts/redesign/python.json`: construção **e serialização**
Python, 3 aquecimentos e 30 repetições alternadas, para 8 e 249 países. O relatório
versionado em `docs/evaluations/map_redesign_python.json` identifica ambiente,
versões e todas as amostras. Essas medições não medem FPS, pintura, interação,
rede, CDN ou latência da LLM. O benchmark de navegador está preparado; seus
resultados e a comparação de fluidez ainda precisam ser registrados.

## Validação e aceite manual pendente

Os testes automatizados cobrem os dados do mapa, escala, transparência, revisão,
escape do tooltip e reutilização da figura, além das regressões do pipeline e UI.
A página inicial foi carregada no Safari em tema escuro; a inspeção do mapa foi
interrompida quando a automação perdeu a janela (`noWindowsAvailable`). Isso não
é evidência de aceite visual do componente.

Execute `.venv/bin/python -m streamlit run src/app.py` e valide:

- [ ] Carregar demonstração: oito países, aviso de dados fictícios, cores e legenda legíveis.
- [ ] Temas claro e escuro: ausência de retângulo/fundo destoante; fronteiras e tooltip legíveis.
- [ ] Desktop e mobile (por exemplo 1440 e 375 px): legenda inteira, tabela e download acessíveis.
- [ ] Zoom, pan, hover e reset: comportamento sem saltos ou captura da rolagem da página.
- [ ] Após zoom, usar o menu Rerun: mesmo resultado e enquadramento, sem consulta à LLM.
- [ ] Alterar o texto sem enviar: resultado anterior preservado; entrada vazia gera aviso.
- [ ] Baixar JSON e conferir países, scores e justificativas com a tabela.
- [ ] Medir antes/depois no benchmark de navegador com 8 e 249 países e registrar resultados.
- [ ] Confirmar os testes manuais antes do merge sem review na `develop`.

Geração real é opcional neste aceite visual e usa a API configurada. A avaliação
empírica dos prompts permanece na issue #4. O papel funcional da JEV foi definido
posteriormente na #8: pesquisa e previsão por evento/prazo para 195 Estados.
O [desenho proposto](JEV_DESIGN.md) ainda exige adaptação do mapa; este redesign
continua usando scores qualitativos e não implementa probabilidades.

A issue #7 permanece aberta até concluir o aceite e registrar as evidências.
