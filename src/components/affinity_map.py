"""Heatmap de afinidade, separado do contrato qualitativo do MVP legado."""

from hashlib import sha256
from html import escape

from plotly.graph_objects import Choropleth, Figure

from src.services.affinity_schema import AffinityResponse

STATE_COLORS = {"filtered_out": "#334155", "insufficient_data": "#94a3b8", "error": "#be185d"}
STATE_LABELS = {"filtered_out": "Excluído por requisito", "insufficient_data": "Dados insuficientes",
                "error": "Erro técnico"}


def plot_affinity_heatmap(response: AffinityResponse) -> Figure:
    response = AffinityResponse.model_validate(response.model_dump())
    figure = Figure(layout={"template": "none"})
    for state, color in STATE_COLORS.items():
        rows = [c for c in response.countries if c.status == state]
        if rows:
            figure.add_trace(Choropleth(
                locations=[c.iso_alpha_3 for c in rows], locationmode="ISO-3", z=[0] * len(rows),
                colorscale=[[0, color], [1, color]], showscale=False, name=STATE_LABELS[state],
                customdata=[[escape(c.name), STATE_LABELS[state]] for c in rows],
                hovertemplate="<b>%{customdata[0]} · %{location}</b><br>%{customdata[1]}<extra></extra>",
                marker_line_color="#0f172a", marker_line_width=0.5,
            ))
    ranked = sorted((c for c in response.countries if c.status == "ranked"), key=lambda c: c.rank)
    if ranked:
        figure.add_trace(Choropleth(
            locations=[c.iso_alpha_3 for c in ranked], locationmode="ISO-3",
            z=[c.affinity_score for c in ranked], coloraxis="coloraxis",
            customdata=[[escape(c.name), c.rank, "Selecionado" if c.selection == "selected" else "Fora do top K"]
                        for c in ranked],
            hovertemplate=("<b>%{customdata[0]} · %{location}</b><br>Afinidade: %{z:.1f} / 100"
                           "<br>Posição: %{customdata[1]} · %{customdata[2]}<extra></extra>"),
            marker_line_color="#0f172a", marker_line_width=0.5,
        ))
    if response.candidate_ids:
        figure.add_trace(Choropleth(
            locations=response.candidate_ids, locationmode="ISO-3", z=[0] * len(response.candidate_ids),
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
            marker_line_color="#f8fafc", marker_line_width=1.6, hoverinfo="skip",
        ))
    revision = sha256(response.model_dump_json().encode()).hexdigest()
    figure.update_geos(
        projection_type="natural earth", projection_rotation={"lon": 0, "lat": 0, "roll": 0},
        center={"lon": 0, "lat": 0}, fitbounds=False, showframe=False, showcoastlines=False,
        showcountries=True, countrycolor="#1e293b", showland=True, landcolor="#172033",
        showocean=False, showlakes=False, bgcolor="rgba(0,0,0,0)", uirevision=revision,
    )
    figure.update_layout(
        height=490, margin={"l": 0, "r": 0, "t": 8, "b": 75},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#cbd5e1"}, hoverlabel={"bgcolor": "#0f172a", "font_color": "#f8fafc"},
        coloraxis={"cmin": 0, "cmax": 100,
                   "colorscale": [[0, "#164e63"], [0.25, "#0891b2"], [0.5, "#2dd4bf"],
                                  [0.75, "#a3e635"], [1, "#fde047"]],
                   "colorbar": {"title": {"text": "Afinidade com o pedido · 0–100", "side": "top"},
                                "orientation": "h", "x": 0.5, "xanchor": "center", "y": -0.02,
                                "len": 0.8, "thickness": 10, "outlinewidth": 0,
                                "tickvals": [0, 25, 50, 75, 100]}},
        uirevision=revision, transition_duration=0,
    )
    return figure
