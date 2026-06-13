# README rewrite audit

## 2026-06-13 web-main update

The README now presents Politiscales Analyser as the primary React/Vite product.
Former Streamlit strings remain below a clearly labelled repository
documentation-contract section so historical tests do not turn legacy anchors
into current product claims.

This file records the repository facts used to regenerate `README.md`.

```json
{
  "dataset": {
    "profile_count": 500,
    "male_count": 352,
    "female_count": 148,
    "unknown_gender_count": 0,
    "family_count": 31,
    "role_count": 16,
    "country_label_count": 143,
    "split_country_token_count": 107,
    "coordinate_audit_count": 7
  },
  "features_detected": {
    "streamlit": true,
    "plotly": true,
    "multiselect_filters": true,
    "json_import_export": true,
    "csv_export": true,
    "dark_sidebar": true,
    "methodology_v3": true
  },
  "paths_detected": [
    "streamlit_app.py",
    "src/political_spectrum_analyzer",
    "src/political_spectrum_analyzer/services",
    "src/political_spectrum_analyzer/services/scoring_model_v3.py",
    "data/reference/personalities.csv",
    "data/reference/ideology_taxonomy.csv",
    "data/reference/ideology_aliases.csv",
    "data/reference/profile_coordinate_audit.csv",
    "docs/reference_dataset_profile_audit.md",
    "docs/assets",
    "tests",
    "requirements.txt",
    "pyproject.toml",
    ".streamlit/config.toml",
    "LICENSE"
  ],
  "license": "custom non-commercial license",
  "remote_origin": "https://github.com/kenzi0228/political-spectrum-analyzer.git"
}
```
