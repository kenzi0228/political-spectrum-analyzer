# Streamlit Cloud Deployment

## Goal

This document prepares the web version of Political Spectrum Analyzer for deployment on Streamlit Community Cloud.

The deployed app uses:

- `streamlit_app.py` as the entry point;
- `requirements.txt` for Python dependencies;
- `.streamlit/config.toml` for theme and server configuration;
- `data/reference/personalities.csv` for the reference dataset.

## Recommended deployment target

Recommended platform:

```text
Streamlit Community Cloud
```

Reason:

- the project is Python-first;
- the app is data-oriented;
- the web version already uses Streamlit;
- no separate backend is required;
- deployment is directly connected to GitHub.

## Deployment settings

Use the following settings:

| Field | Value |
|---|---|
| Repository | `kenzi0228/political-spectrum-analyzer` |
| Branch | `main` |
| Main file path | `streamlit_app.py` |
| Python version | see `runtime.txt` |

## Local deployment check

Before deploying, run:

```powershell
python -m pytest
streamlit run streamlit_app.py
```

The app should open locally and support:

- English / French language selection;
- direct Politiscales link;
- manual numeric score entry;
- slider score entry;
- copied-text import;
- profile JSON import/export;
- multi-profile visualization;
- CSV export.

## OCR policy for deployment

OCR remains desktop-only.

The Streamlit web app must not import or require Tesseract at runtime. This avoids deployment fragility on free hosting platforms.

Expected behavior:

- desktop app can use OCR when dependencies are installed;
- web app uses copied-text import instead;
- Streamlit deployment does not need native Tesseract packages.

## Post-deployment README update

After deployment, update the README with the public Streamlit URL:

```text
Live demo: https://<your-app-name>.streamlit.app
```

Also add screenshots after the live app is verified.