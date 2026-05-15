# Streamlit Cloud Deployment

## Goal

This document describes how to publish the Streamlit web version of Political Spectrum Analyzer.

The app is designed to run on free Streamlit hosting without OCR or native Tesseract dependencies.

## Deployment target

Recommended platform:

```text
Streamlit Community Cloud
```

## App settings

Use these settings:

| Field | Value |
|---|---|
| Repository | `kenzi0228/political-spectrum-analyzer` |
| Branch | `main` |
| Main file path | `streamlit_app.py` |
| Python version | `python-3.12` |
| Dependency file | `requirements.txt` |

## Before deployment

Run locally:

```powershell
python -m py_compile streamlit_app.py
python -m pytest
streamlit run streamlit_app.py
```

Confirm that the web app supports:

- English and French interface;
- Politiscales external link;
- manual numeric score entry;
- slider score entry;
- copied-text import;
- profile JSON import/export;
- multi-profile visualization;
- detailed profile interpretation;
- CSV export.

## OCR policy

OCR is intentionally excluded from the Streamlit runtime.

OCR remains desktop-only.

Reason:

- OCR requires native Tesseract installation;
- free Streamlit deployments should remain lightweight;
- copied-text import already covers the online workflow.

Expected behavior:

- desktop app can use OCR if installed locally;
- Streamlit app does not import `pytesseract`;
- Streamlit app does not import the OCR module;
- deployment depends only on Python packages from `requirements.txt`.

## Public URL

After the app is deployed, copy the generated Streamlit URL and update the README.

Expected format:

```text
https://<your-app-name>.streamlit.app
```

Recommended final commit after deployment:

```text
docs: add live Streamlit demo URL
```

## Post-deployment checks

After deployment, verify online:

- the app opens without dependency errors;
- the language selector works;
- the Politiscales link opens in a new tab;
- a sample profile can be entered manually;
- a saved JSON profile can be imported;
- CSV export works;
- the methodology tab renders correctly.