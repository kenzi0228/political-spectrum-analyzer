# Plotly default reference map and multi-select filters

## Plotly default reference map

The reference map now uses Plotly as the default renderer through `render_default_reference_map(reference_rows)`.

The rendering order is:

1. try the interactive Plotly reference map;
2. fall back to the legacy/static rendering path if Plotly is unavailable.

This keeps Streamlit Cloud interactive while preserving local robustness.

## All reference filters are multi-select

Reference profile filters are now handled through a shared multi-select contract:

```python
REFERENCE_MULTISELECT_FILTER_FIELDS = {
    "ideology_family": "Ideology family",
    "role_category": "Role category",
    "gender": "Gender",
    "country_codes": "Country code",
    "century": "Century",
    "confidence": "Confidence",
}
```

Leaving a filter empty means “do not filter on this field”.

## Gender filter rule

`gender` is available only as a reference-dataset exploration filter. It must never affect scoring, political positioning, interpretation, comparison, or nearest-neighbor distance.
