# Real Streamlit UI integration

## Objective

This commit wires previously added helpers into the actual Streamlit runtime path.

The problem was that several recent commits added helpers, documentation, and tests, but the active `main()` function still used older UI functions. As a result, some features were defined in the file but not visible in the app.

## What is now wired

- `main()` now uses `_render_reference_multiselect_filters(personalities, language)` instead of the older single-selection reference filter path.
- The active reference filters include:
  - country;
  - country code;
  - ideology family;
  - role category;
  - gender;
  - century;
  - confidence.
- Every active reference filter is a real `st.sidebar.multiselect`.
- Empty filters mean “do not filter on this dimension”.
- The graph and reference table use `filtered_personalities`.
- The graph tab uses `_render_integrated_analysis_v3(...)` instead of the old repetitive analysis block.
- The score input mode section has a visible explanatory label before the sidebar options.

## Rule

A feature is only considered done if it is called by the actual Streamlit UI path, not only defined as helpers.
