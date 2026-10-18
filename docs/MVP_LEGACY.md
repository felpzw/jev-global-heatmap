# Legacy Gemini MVP

The original Gemini-scored demonstration is preserved in `src/legacy_app.py`:

```sh
python -m streamlit run src/legacy_app.py
```

It uses Streamlit, Gemini Structured Outputs, Pydantic and Plotly. Gemini generates
countries and qualitative scores directly, without external source retrieval or
guaranteed coverage of the 195-state registry. Its original Portuguese UI,
contract and regression tests are retained as historical reference.

The main application, `src/app.py`, implements the English JEV experience with
local deterministic scores, explicit evidence and optional selected explanations.
See [the README](../README.md), [architecture](../ARCHITECTURE.md) and
[original MVP implementation history](IMPLEMENTATION.md).
