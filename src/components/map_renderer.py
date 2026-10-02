"""Renderização pura: não depende de Streamlit nem chama serviços externos."""

from html import escape
from hashlib import sha256
from textwrap import wrap

from plotly.graph_objects import Choropleth, Figure

from src.services.schema import HeatmapResponse


def plot_heatmap(data: list[dict]) -> Figure:
    validated = HeatmapResponse.model_validate({"countries": data})
    # A stable revision preserves pan/zoom on reruns and resets for new results.
    revision = sha256(validated.model_dump_json().encode()).hexdigest()
    figure = Figure(layout={"template": "none"})
    if validated.countries:
        figure.add_trace(Choropleth(
            locations=[country.iso_alpha_3 for country in validated.countries],
            locationmode="ISO-3",
            z=[country.heat_score for country in validated.countries],
            # Plotly accepts HTML; display model text literally.
            customdata=[[
                "<br>".join(escape(line) for line in wrap(country.context_summary, width=38))
            ] for country in validated.countries],
            hovertemplate=(
                "<b>%{location}</b><br>Intensidade: %{z:.1f} / 100"
                "<br>Contexto: %{customdata[0]}<extra></extra>"
            ),
            coloraxis="coloraxis",
            marker_line_color="#8b939f", marker_line_width=0.5,
        ))
    figure.update_geos(
        projection_type="natural earth", fitbounds=False,
        showframe=False, showcoastlines=False, showcountries=True,
        countrycolor="#8b939f", countrywidth=0.5,
        showland=True, landcolor="#b5bbc5",
        showocean=False, showlakes=False,
        bgcolor="rgba(0,0,0,0)", uirevision=revision,
    )
    figure.update_layout(
        margin={"l": 8, "r": 8, "t": 8, "b": 80}, height=460, autosize=True,
        coloraxis={
            "colorscale": "YlOrRd", "cmin": 0, "cmax": 100,
            "colorbar": {
                "title": {"text": "Intensidade", "side": "top"},
                "orientation": "h", "x": 0.5, "xanchor": "center",
                "y": -0.06, "yanchor": "top", "len": 0.85,
                "thickness": 12, "outlinewidth": 0,
                "tickvals": [0, 25, 50, 75, 100],
            },
        },
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel={"bgcolor": "#17212f", "font_color": "#ffffff"},
        uirevision=revision, transition_duration=0,
    )
    return figure
