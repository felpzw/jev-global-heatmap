"""Renderização pura: não depende de Streamlit nem chama serviços externos."""

from html import escape

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from src.services.schema import HeatmapResponse


def plot_heatmap(data: list[dict]) -> Figure:
    validated = HeatmapResponse.model_validate({"countries": data})
    rows = [country.model_dump() for country in validated.countries]
    # Plotly accepts HTML in hover labels; display model text literally.
    for row in rows:
        row["context_summary"] = escape(row["context_summary"])
    frame = pd.DataFrame(rows, columns=["iso_alpha_3", "heat_score", "context_summary"])
    figure = px.choropleth(
        frame,
        locations="iso_alpha_3",
        locationmode="ISO-3",
        color="heat_score",
        hover_name="iso_alpha_3",
        hover_data={"iso_alpha_3": False, "heat_score": ":.1f", "context_summary": True},
        labels={"heat_score": "Intensidade", "context_summary": "Contexto"},
        color_continuous_scale="YlOrRd",
        range_color=(0, 100),
        projection="natural earth",
    )
    figure.update_geos(
        showframe=False, showcoastlines=False, showcountries=True,
        countrycolor="white", showland=True, landcolor="#e5e7eb",
        showocean=True, oceancolor="#f0f6fa",
    )
    figure.update_layout(
        margin={"l": 0, "r": 0, "t": 12, "b": 0}, height=520,
        coloraxis_colorbar={"title": "Intensidade", "ticksuffix": " / 100"},
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure
