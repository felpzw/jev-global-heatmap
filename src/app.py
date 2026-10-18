"""Run from the project root: python -m streamlit run src/app.py."""

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
from src.services.presentation import CRITERION_LABELS

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    "Coastline + language · preferences": "I prefer countries with a coastline and English as an official language",
    "Coastline required · language preferred": "I require a coastline and prefer English as an official language",
    "Inland · landlocked countries": "I prefer landlocked countries",
    "Explore coastlines": "I prefer countries with a coastline",
    "Clarify beaches and English": "I want beaches and English",
}
ROLES = ["Do not use", "Preference", "Required"]
LABELS = CRITERION_LABELS
STATES = {"ranked": "Ranked", "filtered_out": "Excluded by requirement",
          "insufficient_data": "Insufficient data", "error": "Technical error"}


def set_interpretation(text):
    parsed = interpret(text)
    st.session_state["interpreted_text"] = text.strip()
    st.session_state["questions"] = parsed.questions
    by_id = {c.attribute_id: c for c in parsed.criteria}
    for attr in LABELS:
        criterion = by_id.get(attr)
        st.session_state[f"role_{attr}"] = (
            "Required" if criterion and criterion.role == "requirement"
            else "Preference" if criterion else "Do not use")
        st.session_state[f"expected_{attr}"] = "Yes" if criterion is None or criterion.expected else "No"
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
    st.info(job.get("last_message", "Preparing your search…"))
    if job["future"].done():
        try:
            response = job["future"].result()
            if not job["cancel"].is_set():
                save_result(response)
            else:
                st.session_state["job_notice"] = "Search cancelled. Your previous result has been preserved."
        except RunCancelled:
            st.session_state["job_notice"] = "Search cancelled. Your previous result has been preserved."
        except Exception:
            st.session_state["job_notice"] = "The search could not be completed. Your previous result has been preserved."
        job["executor"].shutdown(wait=False)
        del st.session_state["jev_job"]
        st.rerun()
    st.button("Cancel search", key="cancel_job", on_click=cancel_job)
    st.caption("Cancellation is cooperative; a request already sent to the provider may take up to 30 seconds to finish.")


def launch(request, dataset):
    cache = st.session_state.setdefault("jev_cache", {})
    session = st.session_state.setdefault("jev_session", str(uuid4()))
    checkpoint_dir = ROOT / "artifacts/checkpoints" / session
    if request.local_only:
        with st.spinner("Applying criteria and calculating affinity…"):
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
    st.subheader("One request. A global perspective.")
    st.caption(f"Request for this result: {response.request.text}")
    if response.metadata.dataset_version == "synthetic-demo-v1":
        st.warning("Synthetic demonstration data. These values do not represent facts about the countries.")
    else:
        st.caption("Historical Factbook snapshot · current validity not verified · coastline does not measure beach quality; official language does not measure proficiency.")
    if response.status == "partial":
        st.warning("Ranking preserved. External explanations failed; selected countries use local templates.")
    metrics = st.columns(4)
    metrics[0].metric("States in the registry", len(response.countries))
    metrics[1].metric("Countries scored", counts["ranked"])
    metrics[2].metric("Selected candidates", len(response.candidate_ids))
    metrics[3].metric("Countries to explain", len(response.explanation_ids))
    left, right = st.columns([2.4, 1], gap="large")
    with left:
        st.plotly_chart(stored["figure"], width="stretch", key="affinity_map", on_select="ignore",
                        config={"scrollZoom": False, "displaylogo": False, "responsive": True})
        st.caption("White outline: selected · Dark blue: excluded · Light grey: insufficient data · Pink: error · Background: outside the registry")
        st.caption("Low affinity, including zero, remains on the colour scale. Microstates are in the table; map geometry may not represent them.")
    with right:
        st.markdown("#### Top matches")
        ranked = sorted((c for c in response.countries if c.status == "ranked"), key=lambda c: c.rank)
        if not ranked:
            st.info("No country with complete data meets the requirements. Review the criteria or inspect the gaps below.")
        for c in ranked[:5]:
            st.markdown(f"**{c.rank:02d} · {c.name}**")
            st.progress(c.affinity_score / 100, text=f"{c.affinity_score:.1f} / 100 · {c.iso_alpha_3}")
        st.caption("Ties are broken alphabetically by ISO code. Tied countries have no evidence-based difference in score.")
        st.caption(f"{counts['filtered_out']} excluded by requirement · {counts['insufficient_data']} with insufficient data")
    ranking_tab, evidence_tab, run_tab = st.tabs(["Ranking and status", "Criteria and sources", "Run details and export"])
    by_iso = {c.iso_alpha_3: c for c in response.countries}
    with ranking_tab:
        query = st.text_input("Search by country or ISO code", key="country_search").casefold().strip()
        states = st.multiselect("Show statuses", list(STATES), default=list(STATES),
                                format_func=lambda s: STATES[s], key="status_filter")
        rows = sorted(response.countries, key=lambda c: (c.rank is None, c.rank or 0, c.iso_alpha_3))
        table = [{"Rank": c.rank, "Country": c.name, "ISO": c.iso_alpha_3,
                  "Affinity": c.affinity_score, "Status": STATES[c.status],
                  "Selected": c.selection == "selected", "Explanation": c.explanation_source or "Not requested"}
                 for c in rows if c.status in states and (not query or query in c.name.casefold() or query in c.iso_alpha_3.casefold())]
        st.dataframe(table, hide_index=True, width="stretch",
                     column_config={"Affinity": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f")})
    with evidence_tab:
        iso = st.selectbox("Inspect a country", list(by_iso), format_func=lambda x: f"{by_iso[x].name} · {x}", key="inspect_country")
        country = by_iso[iso]
        st.write(country.reason)
        if country.explanation:
            st.info(country.explanation.text)
            st.caption(f"Source: {country.explanation_source} · status: {country.explanation_status}")
        st.dataframe([{"Criterion": LABELS[f.criterion.attribute_id], "Role": f.criterion.role,
                       "Desired": f.criterion.expected, "Observed": f.evidence.value,
                       "Weight": f.criterion.weight, "Normalized": f.normalized,
                       "Contribution": f.contribution, "Data status": f.evidence.data_status,
                       "Evidence": f.evidence.evidence_id} for f in country.factors], hide_index=True, width="stretch")
        for factor in country.factors:
            evidence = factor.evidence
            with st.expander(f"{LABELS[factor.criterion.attribute_id]} · provenance"):
                st.write(evidence.reason)
                if evidence.source_url and "example.invalid" not in evidence.source_url:
                    st.link_button("Open pinned source", evidence.source_url)
                st.json(evidence.model_dump())
    with run_tab:
        st.write("The score measures affinity with the confirmed criteria. It is not a probability and should not be compared across different requests.")
        st.caption("local_only covers the engine and explanations. The Plotly basemap requires CDN geometry in your browser.")
        st.json({"run_id": response.run_id, "status": response.status,
                 "request": response.request.model_dump(), "metadata": response.metadata.model_dump(),
                 "candidate_ids": response.candidate_ids, "explanation_ids": response.explanation_ids}, expanded=False)
        st.download_button("Download result JSON", response.model_dump_json(indent=2),
                           file_name=f"jev-affinity-{response.run_id[:8]}.json", mime="application/json")


def main():
    st.set_page_config(page_title="JEV · Global Concept Search", page_icon="🌐", layout="wide")
    if st.session_state.get("ui_language") != "en":
        # Migrate widgets in open sessions when the English release is hot-reloaded.
        cancel_job()
        for key in ("example", "dataset"):
            st.session_state.pop(key, None)
        if "affinity_result" in st.session_state:
            st.session_state["previous_language_result"] = st.session_state.pop("affinity_result")
            st.session_state["job_notice"] = "The interface is now in English. Recalculate to refresh your result."
        st.session_state.setdefault("context", EXAMPLES[next(iter(EXAMPLES))])
        set_interpretation(st.session_state["context"])
        st.session_state["ui_language"] = "en"
    with st.sidebar:
        st.markdown("### JEV / GLOBAL")
        st.caption("EXPLAINABLE CONCEPT SEARCH")
        example = st.selectbox("Start with an idea", list(EXAMPLES), key="example")
        if st.button("Use example", key="use_example", width="stretch"):
            st.session_state["context"] = EXAMPLES[example]
            set_interpretation(EXAMPLES[example])
        st.divider()
        dataset_label = st.selectbox("Dataset", ["Factbook · historical snapshot", "Synthetic demonstration"], key="dataset")
        local_only = st.toggle("Local engine only", value=True, key="local_only")
        if local_only:
            st.caption("Ranking and explanations without an API. The map uses a CDN in your browser.")
        else:
            st.caption("Gemini explains selected countries over the network. Without a key, local templates are used.")
        with st.expander("Selection limits"):
            threshold = st.slider("Minimum affinity", 0, 100, 50, key="threshold")
            candidate_limit = st.slider("Maximum candidates", 1, 20, 20, key="candidate_limit")
            explanation_limit = st.slider("Maximum explanations", 0, 10, 10, key="explanation_limit")
        st.divider()
        st.caption("How it works")
        st.write("01 · Interpret your request\n\n02 · Confirm criteria and weights\n\n03 · Explore the map and evidence")
        st.link_button("Code and documentation", "https://github.com/felpzw/jev-global-heatmap", width="stretch")
    st.caption("JEV LAB / INTERACTIVE PORTFOLIO")
    st.title("Connect an idea to the world.")
    st.write("Turn criteria into a global affinity map: traceable data, visible weights and explanations for the top matches.")
    st.caption("Starter catalog: maritime coastline and English as an official national language. New concepts require new criteria and sources.")
    if "context" not in st.session_state:
        st.session_state["context"] = EXAMPLES[next(iter(EXAMPLES))]
        set_interpretation(st.session_state["context"])
    with st.form("interpret_form"):
        text = st.text_area("What are you looking for?", key="context", height=85, max_chars=4000,
                            placeholder="E.g. I require a coastline and prefer English as an official language")
        submitted = st.form_submit_button("Interpret request")
    if submitted:
        set_interpretation(text)
    if "job_notice" in st.session_state:
        st.info(st.session_state.pop("job_notice"))
    if text.strip() == st.session_state.get("interpreted_text") and text.strip():
        st.markdown("#### Review how JEV interpreted your request")
        questions = st.session_state.get("questions", [])
        for question in questions:
            st.warning(question)
        with st.form("confirm_form"):
            criteria = []
            for attr, label in LABELS.items():
                name_col, role_col, expected_col, weight_col = st.columns([2, 1.5, 1, 1])
                name_col.markdown(f"**{label}**")
                role = role_col.selectbox(f"Role · {label}", ROLES, key=f"role_{attr}")
                expected = expected_col.selectbox(f"Desired · {label}", ["Yes", "No"], key=f"expected_{attr}")
                weight = weight_col.number_input(f"Weight · {label}", min_value=0.1, max_value=100.0,
                                                 step=0.5, key=f"weight_{attr}")
                if role != "Do not use":
                    criteria.append(Criterion(attribute_id=attr, expected=expected == "Yes",
                        role="requirement" if role == "Required" else "preference", weight=weight))
            st.caption("Requirements filter countries; only preferences contribute to the weighted average. Missing data never becomes zero.")
            confirmed = st.checkbox("I confirm these criteria and the catalog scope", key="confirmed")
            execute = st.form_submit_button("Calculate global affinity", type="primary",
                                            disabled="jev_job" in st.session_state)
        if execute:
            if not confirmed:
                st.warning("Confirm the criteria before running the search.")
            else:
                try:
                    request = AffinityRequest(text=text.strip(), criteria=criteria, confirmed=True,
                        local_only=local_only, threshold=float(threshold), candidate_limit=candidate_limit,
                        explanation_limit=explanation_limit)
                    dataset = load_demo_dataset() if dataset_label == "Synthetic demonstration" else load_dataset()
                    launch(request, dataset)
                except ValueError:
                    st.error("Review the criteria: include at least one preference and keep explanations within the candidate limit. Also check dataset integrity.")
    elif text.strip():
        st.info("Interpret the new request to review its criteria before calculating.")
    else:
        st.info("Enter a request to get started.")
    if "jev_job" in st.session_state:
        pending_job()
    if "affinity_result" in st.session_state:
        render_result()
    else:
        st.info("Confirm the criteria to explore the 195 states in the registry. Try it without an API key.")


if __name__ == "__main__":
    main()
