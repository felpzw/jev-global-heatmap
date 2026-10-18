# MVP executável — Gemini e intensidade qualitativa

O MVP preservado em `src/legacy_app.py` usa Streamlit, Gemini Structured Outputs, Pydantic e Plotly.
Execute `python -m streamlit run src/legacy_app.py`. A aplicação principal em `src/app.py` já usa o motor JEV.
Recebe contexto livre e produz heat_score de 0 a 100, não probabilidades.
Não consulta fontes, não garante os 195 e não implementa a nova JEV.

Pontos: src/app.py, src/services/llm_client.py, schema.py, prompts.py e
src/components/map_renderer.py. Há demonstração fictícia, sessão preservada,
tabela e download. O contexto é limitado a 4.000 caracteres; a saída a 8.192
tokens; o prompt prefere até 40 países. HeatmapResponse aceita até 249 códigos
válidos de pycountry, que inclui territórios fora do novo universo.

Falhas/truncamentos não substituem o resultado anterior. Reruns não geram nova
consulta. As geometrias atuais vêm de CDN. A suíte offline de 29 testes passou
em 05/10/2026, sem demonstrar qualidade factual nem a arquitetura nova.

Instalação permanece no README; use o comando legado acima. Histórico do MVP em
[IMPLEMENTATION.md](IMPLEMENTATION.md) e prompts em [PROMPT_DESIGN.md](PROMPT_DESIGN.md).
As propostas anteriores foram [arquivadas](legacy/README.md). A direção atual
é [ranking de afinidade](adr/0003-affinity-ranking.md), implementado no catálogo inicial.
Veja [DELIVERY.md](DELIVERY.md) para evidências e limitações.
