"""Execute na raiz: python -m streamlit run src/app.py."""

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Empty, Queue
from threading import Event
from uuid import uuid4

import streamlit as st

from src.components.affinity_map import plot_affinity_heatmap
from src.services.affinity_ranker import RunCancelled
from src.services.affinity_schema import AffinityRequest, AffinityResponse, Criterion
from src.services.evidence_service import load_dataset, load_demo_dataset
from src.services.input_parser import interpret
from src.services.jev_service import run_affinity

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    "Litoral + idioma · preferências": "Prefiro litoral e inglês oficial",
    "Litoral obrigatório · idioma preferido": "Exijo litoral e prefiro inglês oficial",
    "Interior · sem litoral": "Prefiro países sem litoral",
    "Explorar litoral": "Prefiro países com litoral",
    "Esclarecer praia e inglês": "Quero praia e inglês",
}
ROLES = ["Não usar", "Preferência", "Obrigatório"]
LABELS = {"has_maritime_coast": "Litoral marítimo", "english_official": "Inglês oficial nacional"}
STATES = {"ranked": "Com score", "filtered_out": "Excluído por requisito",
          "insufficient_data": "Dados insuficientes", "error": "Erro técnico"}


def set_interpretation(text):
    parsed = interpret(text)
    st.session_state["interpreted_text"] = text.strip()
    st.session_state["questions"] = parsed.questions
    by_id = {c.attribute_id: c for c in parsed.criteria}
    for attr in LABELS:
        criterion = by_id.get(attr)
        st.session_state[f"role_{attr}"] = (
            "Obrigatório" if criterion and criterion.role == "requirement"
            else "Preferência" if criterion else "Não usar")
        st.session_state[f"expected_{attr}"] = "Sim" if criterion is None or criterion.expected else "Não"
        st.session_state[f"weight_{attr}"] = 1.0
    st.session_state["confirmed"] = False


def save_result(response):
    st.session_state["affinity_result"] = {
        "response": response.model_dump(), "figure": plot_affinity_heatmap(response),
    }


def cancel_job():
    job = st.session_state.get("jev_job")
    if job:
        job["cancel"].set()


@st.fragment(run_every="500ms")
def pending_job():
    job = st.session_state.get("jev_job")
    if not job:
        return
    messages = []
    try:
        while True:
            messages.append(job["messages"].get_nowait())
    except Empty:
        pass
    if messages:
        job["last_message"] = messages[-1]
    st.info(job.get("last_message", "Preparando a execução…"))
    if job["future"].done():
        try:
            response = job["future"].result()
            if not job["cancel"].is_set():
                save_result(response)
            else:
                st.session_state["job_notice"] = "Execução cancelada. O resultado anterior foi preservado."
        except RunCancelled:
            st.session_state["job_notice"] = "Execução cancelada. O resultado anterior foi preservado."
        except Exception:
            st.session_state["job_notice"] = "Não foi possível concluir. O resultado anterior foi preservado."
        job["executor"].shutdown(wait=False)
        del st.session_state["jev_job"]
        st.rerun()
    st.button("Cancelar execução", key="cancel_job", on_click=cancel_job)
    st.caption("Cancelamento cooperativo; uma chamada já enviada pode levar até 30 s para terminar.")


def launch(request, dataset):
    cache = st.session_state.setdefault("jev_cache", {})
    session = st.session_state.setdefault("jev_session", str(uuid4()))
    checkpoint_dir = ROOT / "artifacts/checkpoints" / session
    if request.local_only:
        with st.spinner("Aplicando critérios e calculando afinidade…"):
            save_result(run_affinity(request, dataset=dataset, cache=cache, checkpoint_dir=checkpoint_dir))
    else:
        messages, cancel = Queue(), Event()
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(run_affinity, request, dataset=dataset, cache=cache,
                                 checkpoint_dir=checkpoint_dir, cancelled=cancel.is_set,
                                 progress=messages.put)
        st.session_state["jev_job"] = {"future": future, "executor": executor,
                                       "messages": messages, "cancel": cancel}


def render_result():
    stored = st.session_state["affinity_result"]
    response = AffinityResponse.model_validate(stored["response"])
    counts = Counter(c.status for c in response.countries)
    st.divider()
    st.subheader("Um pedido. Uma visão global.")
    st.caption(f"Pedido deste resultado: {response.request.text}")
    if response.metadata.dataset_version == "synthetic-demo-v1":
        st.warning("Demonstração com dados fictícios. Estes valores não representam fatos sobre os países.")
    else:
        st.caption("Snapshot histórico do Factbook · vigência atual não verificada · litoral não mede praia; idioma não mede proficiência.")
    if response.status == "partial":
        st.warning("Ranking preservado. A explicação externa falhou; os selecionados usam templates locais.")
    metrics = st.columns(4)
    metrics[0].metric("Estados no registro", len(response.countries))
    metrics[1].metric("Com afinidade calculada", counts["ranked"])
    metrics[2].metric("Candidatos selecionados", len(response.candidate_ids))
    metrics[3].metric("Países para justificar", len(response.explanation_ids))
    left, right = st.columns([2.4, 1], gap="large")
    with left:
        st.plotly_chart(stored["figure"], width="stretch", key="affinity_map", on_select="ignore",
                        config={"scrollZoom": False, "displaylogo": False, "responsive": True})
        st.caption("Contorno branco: selecionados · Azul escuro: exclusão · Cinza claro: dados insuficientes · Rosa: erro · Fundo: fora do registro")
        st.caption("Baixa afinidade, inclusive zero, permanece na escala de cores. Microestados estão na tabela; a geometria pode não representá-los.")
    with right:
        st.markdown("#### No topo do pedido")
        ranked = sorted((c for c in response.countries if c.status == "ranked"), key=lambda c: c.rank)
        if not ranked:
            st.info("Nenhum país com dados completos atende aos requisitos. Revise os critérios ou consulte as lacunas abaixo.")
        for c in ranked[:5]:
            st.markdown(f"**{c.rank:02d} · {c.name}**")
            st.progress(c.affinity_score / 100, text=f"{c.affinity_score:.1f} / 100 · {c.iso_alpha_3}")
        st.caption("Empates: código ISO em ordem alfabética. Não há distinção factual entre países empatados.")
        st.caption(f"{counts['filtered_out']} excluídos por requisito · {counts['insufficient_data']} com dados insuficientes")
    ranking_tab, evidence_tab, run_tab = st.tabs(["Ranking e estados", "Critérios e fontes", "Execução e exportação"])
    by_iso = {c.iso_alpha_3: c for c in response.countries}
    with ranking_tab:
        query = st.text_input("Buscar país ou código ISO", key="country_search").casefold().strip()
        states = st.multiselect("Estados exibidos", list(STATES), default=list(STATES),
                                format_func=lambda s: STATES[s], key="status_filter")
        rows = sorted(response.countries, key=lambda c: (c.rank is None, c.rank or 0, c.iso_alpha_3))
        table = [{"Posição": c.rank, "País": c.name, "ISO": c.iso_alpha_3,
                  "Afinidade": c.affinity_score, "Estado": STATES[c.status],
                  "Selecionado": c.selection == "selected", "Justificativa": c.explanation_source or "Não solicitada"}
                 for c in rows if c.status in states and (not query or query in c.name.casefold() or query in c.iso_alpha_3.casefold())]
        st.dataframe(table, hide_index=True, width="stretch",
                     column_config={"Afinidade": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f")})
    with evidence_tab:
        iso = st.selectbox("Inspecionar país", list(by_iso), format_func=lambda x: f"{by_iso[x].name} · {x}", key="inspect_country")
        country = by_iso[iso]
        st.write(country.reason)
        if country.explanation:
            st.info(country.explanation.text)
            st.caption(f"Origem: {country.explanation_source} · estado: {country.explanation_status}")
        st.dataframe([{"Critério": LABELS[f.criterion.attribute_id], "Papel": f.criterion.role,
                       "Desejado": f.criterion.expected, "Observado": f.evidence.value,
                       "Peso": f.criterion.weight, "Normalizado": f.normalized,
                       "Contribuição": f.contribution, "Dado": f.evidence.data_status,
                       "Evidência": f.evidence.evidence_id} for f in country.factors], hide_index=True, width="stretch")
        for factor in country.factors:
            evidence = factor.evidence
            with st.expander(f"{LABELS[factor.criterion.attribute_id]} · proveniência"):
                st.write(evidence.reason)
                if evidence.source_url and "example.invalid" not in evidence.source_url:
                    st.link_button("Abrir fonte fixada", evidence.source_url)
                st.json(evidence.model_dump())
    with run_tab:
        st.write("O score mede afinidade com os critérios confirmados. Não é probabilidade e não deve ser comparado entre pedidos diferentes.")
        st.caption("local_only cobre o motor e as explicações. O mapa base do Plotly requer geometrias do CDN no navegador.")
        st.json({"run_id": response.run_id, "status": response.status,
                 "request": response.request.model_dump(), "metadata": response.metadata.model_dump(),
                 "candidate_ids": response.candidate_ids, "explanation_ids": response.explanation_ids}, expanded=False)
        st.download_button("Baixar resultado JSON", response.model_dump_json(indent=2),
                           file_name=f"jev-affinity-{response.run_id[:8]}.json", mime="application/json")


def main():
    st.set_page_config(page_title="JEV · Global Concept Search", page_icon="🌐", layout="wide")
    with st.sidebar:
        st.markdown("### JEV / GLOBAL")
        st.caption("BUSCA CONCEITUAL EXPLICÁVEL")
        example = st.selectbox("Comece por uma ideia", list(EXAMPLES), key="example")
        if st.button("Usar exemplo", key="use_example", width="stretch"):
            st.session_state["context"] = EXAMPLES[example]
            set_interpretation(EXAMPLES[example])
        st.divider()
        dataset_label = st.selectbox("Dados", ["Factbook · snapshot histórico", "Demonstração fictícia"], key="dataset")
        local_only = st.toggle("Somente motor local", value=True, key="local_only")
        if local_only:
            st.caption("Ranking e justificativas sem API. O mapa usa CDN no navegador.")
        else:
            st.caption("Gemini explica os selecionados via rede. Sem chave, usamos templates.")
        with st.expander("Limites da seleção"):
            threshold = st.slider("Afinidade mínima", 0, 100, 50, key="threshold")
            candidate_limit = st.slider("Máximo de candidatos", 1, 20, 20, key="candidate_limit")
            explanation_limit = st.slider("Máximo de justificativas", 0, 10, 10, key="explanation_limit")
        st.divider()
        st.caption("Como funciona")
        st.write("01 · Interprete o pedido\n\n02 · Confirme critérios e pesos\n\n03 · Explore mapa e evidências")
        st.link_button("Código e documentação", "https://github.com/felpzw/jev-global-heatmap", width="stretch")
    st.caption("JEV LAB / PORTFÓLIO INTERATIVO")
    st.title("Conecte uma ideia ao mundo.")
    st.write("Transforme critérios em um mapa de afinidade: dados rastreáveis, pesos visíveis e explicações para os melhores resultados.")
    st.caption("Catálogo inicial: litoral marítimo e inglês oficial nacional. Novos conceitos exigem novos critérios e fontes.")
    if "context" not in st.session_state:
        st.session_state["context"] = EXAMPLES[next(iter(EXAMPLES))]
        set_interpretation(st.session_state["context"])
    with st.form("interpret_form"):
        text = st.text_area("O que você procura?", key="context", height=85, max_chars=4000,
                            placeholder="Ex.: exijo litoral e prefiro inglês oficial")
        submitted = st.form_submit_button("Interpretar pedido")
    if submitted:
        set_interpretation(text)
    if "job_notice" in st.session_state:
        st.info(st.session_state.pop("job_notice"))
    if text.strip() == st.session_state.get("interpreted_text") and text.strip():
        st.markdown("#### Revise o que a JEV entendeu")
        questions = st.session_state.get("questions", [])
        for question in questions:
            st.warning(question)
        with st.form("confirm_form"):
            criteria = []
            for attr, label in LABELS.items():
                name_col, role_col, expected_col, weight_col = st.columns([2, 1.5, 1, 1])
                name_col.markdown(f"**{label}**")
                role = role_col.selectbox(f"Papel · {label}", ROLES, key=f"role_{attr}")
                expected = expected_col.selectbox(f"Desejado · {label}", ["Sim", "Não"], key=f"expected_{attr}")
                weight = weight_col.number_input(f"Peso · {label}", min_value=0.1, max_value=100.0,
                                                 step=0.5, key=f"weight_{attr}")
                if role != "Não usar":
                    criteria.append(Criterion(attribute_id=attr, expected=expected == "Sim",
                        role="requirement" if role == "Obrigatório" else "preference", weight=weight))
            st.caption("Requisitos filtram; apenas preferências entram na média ponderada. Ausência de dados nunca vira zero.")
            confirmed = st.checkbox("Confirmo estes critérios e o escopo do catálogo", key="confirmed")
            execute = st.form_submit_button("Calcular afinidade global", type="primary",
                                            disabled="jev_job" in st.session_state)
        if execute:
            if not confirmed:
                st.warning("Confirme os critérios antes de executar.")
            else:
                try:
                    request = AffinityRequest(text=text.strip(), criteria=criteria, confirmed=True,
                        local_only=local_only, threshold=float(threshold), candidate_limit=candidate_limit,
                        explanation_limit=explanation_limit)
                    dataset = load_demo_dataset() if dataset_label == "Demonstração fictícia" else load_dataset()
                    launch(request, dataset)
                except ValueError:
                    st.error("Revise os critérios: use ao menos uma preferência e limite as justificativas ao número de candidatos. Verifique também a integridade do dataset.")
    elif text.strip():
        st.info("Interprete o novo pedido para revisar os critérios antes de calcular.")
    else:
        st.info("Informe um pedido para começar.")
    if "jev_job" in st.session_state:
        pending_job()
    if "affinity_result" in st.session_state:
        render_result()
    else:
        st.info("Confirme os critérios para explorar os 195 Estados no mapa. Você pode experimentar sem configurar uma chave.")


if __name__ == "__main__":
    main()
