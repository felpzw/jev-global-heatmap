"""Execute na raiz: python -m streamlit run src/app.py."""

from pathlib import Path

import streamlit as st

from src.components.map_renderer import plot_heatmap
from src.services.llm_client import HeatmapError, MAX_CONTEXT_LENGTH, generate_heatmap
from src.services.schema import HeatmapResponse


def save_result(response: HeatmapResponse, context: str, source: str) -> None:
    st.session_state["mapping"] = {
        "response": response.model_dump(), "context": context, "source": source,
    }


def main() -> None:
    st.set_page_config(page_title="JEV Global Heatmap", page_icon="🌍", layout="wide")
    st.title("JEV Global Heatmap")
    st.write("Explore a relevância de um tema pelo mundo.")
    st.caption(
        "Os scores da IA são estimativas qualitativas, sem consulta a fontes em tempo real. "
        "Países em cinza não têm dados; isso não significa intensidade zero."
    )

    with st.sidebar:
        st.header("Experimente o mapa")
        st.write("Veja oito países com dados fictícios, sem precisar configurar uma chave.")
        if st.button("Carregar demonstração", key="demo"):
            fixture = Path(__file__).resolve().parents[1] / "data/demo_heatmap.json"
            save_result(
                HeatmapResponse.model_validate_json(fixture.read_text(encoding="utf-8")),
                "Cenário de demonstração", "demo",
            )

    with st.form("research_form"):
        context = st.text_area(
            "Contexto de pesquisa", key="context", max_chars=MAX_CONTEXT_LENGTH,
            placeholder="Ex.: adoção de carros elétricos; considere a participação na frota por país.",
            height=120,
        )
        submitted = st.form_submit_button("Gerar Mapeamento", type="primary")

    if submitted:
        if not context.strip():
            st.warning("Informe um contexto de pesquisa antes de gerar o mapeamento.")
        else:
            try:
                with st.spinner("Analisando o contexto e validando os países…"):
                    response = generate_heatmap(context)
                save_result(response, context.strip(), "gemini")
            except HeatmapError as error:
                st.error(str(error))
                if "mapping" in st.session_state:
                    st.info("O resultado anterior foi preservado e continua identificado abaixo.")

    if "mapping" not in st.session_state:
        st.info("Descreva um tema para gerar o mapa ou carregue a demonstração.")
        return

    mapping = st.session_state["mapping"]
    data = mapping["response"]["countries"]
    st.subheader("Resultado")
    st.text(f"Contexto: {mapping['context']}")
    if mapping["source"] == "demo":
        st.warning("Demonstração com dados fictícios. Estes scores não representam uma pesquisa real.")
    if not data:
        st.info("Não há países com contexto suficiente para este tema. Acrescente detalhes à pesquisa.")
        return

    st.caption(f"{len(data)} países/territórios · Intensidade de 0 a 100")
    st.plotly_chart(plot_heatmap(data), width="stretch", key="heatmap")
    with st.expander("Ver dados e justificativas"):
        st.dataframe(data, hide_index=True, width="stretch")
    st.download_button(
        "Baixar resultado JSON",
        data=HeatmapResponse.model_validate(mapping["response"]).model_dump_json(indent=2),
        file_name="jev-heatmap.json", mime="application/json",
    )


if __name__ == "__main__":
    main()
