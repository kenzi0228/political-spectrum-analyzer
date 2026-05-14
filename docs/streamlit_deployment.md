# Streamlit Deployment Guide

## 1. Purpose

This document explains how to deploy the web version of Political Spectrum Analyzer.

The desktop version remains available through Tkinter. The web version is implemented with Streamlit and Plotly.

---

## 2. Recommended hosting option

The recommended free hosting option is:

```text
Streamlit Community Cloud
```

It is suitable for this project because:

- the project is Python-based;
- the app is data-oriented;
- Streamlit can run directly from a GitHub repository;
- no separate frontend/backend architecture is required;
- the existing Python services can be reused.

---

## 3. Entry point

The Streamlit entry point is:

```text
streamlit_app.py
```

To run locally:

```powershell
streamlit run streamlit_app.py
```

---

## 4. Dependencies

Deployment dependencies are declared in:

```text
requirements.txt
```

The web application requires at least:

```text
streamlit
plotly
pandas
matplotlib
```

The OCR dependencies may exist in the project for the desktop app, but OCR is intentionally not used in the web version.

---

## 5. OCR limitation on web hosting

Screenshot OCR is excluded from the Streamlit web version.

Reason:

- OCR requires the native Tesseract executable;
- free hosting platforms may not provide Tesseract by default;
- native binary setup increases deployment fragility;
- copied-text import is more reliable for the web app.

The web version keeps copied-text import as the recommended import mode.

---

## 6. Deploying to Streamlit Community Cloud

Steps:

1. Push the repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app.
4. Select the GitHub repository.
5. Select the `main` branch.
6. Set the main file path to:

```text
streamlit_app.py
```

7. Deploy.

---

## 7. Local verification before deployment

Before deploying, run:

```powershell
python -m pytest
streamlit run streamlit_app.py
```

The app should open locally in the browser.

---

## 8. Expected web features

The web app supports:

- manual score input;
- copied-text import;
- interactive Plotly visualization;
- reference filters;
- position analysis;
- closest-reference analysis;
- CSV export;
- reference dataset browser;
- methodology summary.

---

## 9. Known differences from the desktop version

| Feature | Desktop | Web |
|---|---:|---:|
| Manual input | yes | yes |
| Copied-text import | yes | yes |
| OCR screenshot import | yes | no |
| Interactive Plotly graph | no | yes |
| CSV export | yes | yes |
| Reference filters | yes | yes |
| Local Tkinter UI | yes | no |

---

## 10. Post-deployment checklist

After deployment:

- verify the app loads correctly;
- test manual score input;
- test copied-text import;
- test reference filters;
- test CSV download;
- check that the README contains the public app URL;
- add screenshots to the README.