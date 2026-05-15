# Release Notes â€” v1 Desktop + Web Preview

## Status

This release marks the project as stable enough for portfolio presentation.

The repository now contains:

- a desktop Tkinter application;
- a Streamlit web application;
- tested scoring and analysis services;
- a structured reference dataset;
- documentation;
- CI configuration;
- packaging metadata.

---

## Main features

### Desktop application

- Manual input of 16 ideological scores.
- Copied-text import from Politiscales-style results.
- Optional OCR screenshot import.
- 2D political spectrum visualization.
- Reference personality filtering.
- Automatic profile analysis.
- Closest-reference calculation.
- PNG chart export.
- Configurable CSV export.

### Web application

- Streamlit interface.
- Manual score input.
- Copied-text import.
- Interactive Plotly visualization.
- Reference filters.
- Analysis metrics.
- Closest-reference table.
- CSV download.
- Reference dataset browser.

OCR is intentionally desktop-only.

---

## Dataset

The project includes a curated reference dataset of 150 personalities with:

- group;
- country or countries;
- period;
- ideology family;
- coordinates;
- uncertainty values;
- confidence level;
- notes.

The dataset is heuristic and intended for exploratory comparison.

---

## Testing and quality

The project includes tests for:

- scoring;
- validation;
- text import;
- OCR optional behavior;
- analysis;
- CSV export;
- dataset quality;
- filter behavior;
- documentation;
- package entry point;
- Plotly web plotting.

---

## Known limitations

- The political projection is heuristic.
- Reference placements are approximate.
- The 2D map simplifies complex political ideologies.
- OCR depends on local Tesseract availability.
- The Streamlit web version excludes OCR for deployment reliability.

---

## Suggested next steps

- Add screenshots to the README.
- Add a public Streamlit deployment URL after deployment.
- Create a GitHub release tag.
- Add source citations for each reference personality in a future version.