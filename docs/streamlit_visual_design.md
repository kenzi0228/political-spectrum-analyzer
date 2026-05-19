# Streamlit visual design

This document tracks the visual upgrade for the deployed Streamlit application.

## Theme

The app uses a custom Streamlit theme in `.streamlit/config.toml`:

- dark background;
- violet primary accent;
- high-contrast text;
- darker secondary surface for panels and containers.

## Custom CSS layer

`streamlit_app.py` includes a lightweight CSS layer for:

- metric cards;
- tabs;
- buttons;
- sidebar surface;
- hero section;
- rounded panel styling.

## Plotly direction

The project now includes an optional Plotly reference-map helper:

```python
build_reference_plotly_figure(reference_data)
render_reference_plotly_chart(reference_data)
```

Plotly is used for interactive exploration: hover, zoom, pan, legend filtering, and richer tooltip metadata.

## Compatibility rule

Plotly must remain optional at import time. If the environment does not provide Plotly, the app should still import successfully and keep existing non-Plotly rendering paths available.
