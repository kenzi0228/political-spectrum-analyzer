# Political Spectrum Analyzer

Political Spectrum Analyzer is a Streamlit application for converting Politiscales-style political scores into a readable political profile, a two-dimensional graph position, and comparisons against reference personalities.


Repository: `https://github.com/kenzi0228/political-spectrum-analyzer.git`

This README is based on the current repository state. It does not add unverified deployment URLs, performance metrics, screenshots, or features that are not represented by local files.

---

## What the project does

The app lets a user enter or import political-test scores, visualize the resulting position, compare profiles, and explore nearby reference personalities.

- Interactive Streamlit interface for creating and comparing political profiles.
- Reference map against the local reference-personality dataset.
- Detailed profile interpretation based on the full 16-axis score structure.
- Plotly-based visualization layer for the reference map.
- Multi-select reference filters for metadata-driven exploration.
- JSON import/export workflow for reusing profiles locally.
- CSV export path for structured results.
- Dark sidebar styling for readable controls.
- Methodology tab documenting the current scoring model v3.

---

## Current dataset status

The current reference dataset contains **500 profiles**.

Gender metadata currently contains:

- **352 male** profiles
- **148 female** profiles
- **0 unknown** values

Additional dataset structure detected:

- ideology families: **31**
- role categories: **16**
- countries / country labels: **143**

The coordinate audit currently flags **7 profiles** for later manual review.

Core reference data:

```text
data/reference/personalities.csv
```

Coordinate-audit artifacts:

```text
data/reference/profile_coordinate_audit.csv
docs/reference_dataset_profile_audit.md
```

---

## Scoring methodology

The current methodology uses scoring model v3. It builds weighted ideological blocks, compares opposite blocks, applies limited secondary adjustments, then normalizes the result into the graph range `[-4, 4]`.

### Economic blocks

```text
economic_left =
    0.95 * communisme
  + 0.75 * regulation
  + 0.38 * ecologie

economic_right =
    0.95 * capitalisme
  + 0.80 * laissez_faire
  + 0.32 * productivisme
```

### Social-authority blocks

```text
social_libertarian =
    0.75 * constructivisme
  + 0.70 * justice_rehabilitative
  + 0.75 * progressisme
  + 0.45 * internationalisme

social_authoritarian =
    0.65 * essentialisme
  + 0.75 * justice_punitive
  + 0.75 * conservatisme
  + 0.45 * nationalisme
```

### Raw axes and normalization

```text
economic_raw = economic_right - economic_left
social_raw = social_authoritarian - social_libertarian

economic_raw += 0.10 * (productivisme - ecologie)
social_raw += 0.06 * (nationalisme - internationalisme)

x = 4 * tanh(0.015 * economic_raw)
y = 4 * tanh(0.015 * social_raw)
```

`revolution` and `reformisme` are kept for detailed interpretation of political strategy. They are not direct coordinate markers.

Implementation:

```text
src/political_spectrum_analyzer/services/scoring_model_v3.py
```

---

## Main application flow

1. Create a political profile from score values.
2. Review the computed `x` and `y` graph coordinates.
3. Read the detailed profile interpretation.
4. Compare profiles when several profiles are entered.
5. Explore nearby reference personalities.
6. Filter reference personalities by available metadata.
7. Export or reuse structured results when the UI exposes an export option.

---

## Local setup

### 1. Clone the repository

```powershell
git clone https://github.com/kenzi0228/political-spectrum-analyzer.git
cd political-spectrum-analyzer
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the Streamlit app

```powershell
streamlit run streamlit_app.py
```

---

## Tests

Run the full regression suite with:

```powershell
python -m pytest
```

The suite covers scoring services, dataset schema and quality rules, Streamlit integration contracts, import/export services, methodology content, and reference-dataset regressions.

---

## Repository structure

Detected project paths:

- `streamlit_app.py`
- `src/political_spectrum_analyzer`
- `src/political_spectrum_analyzer/services`
- `src/political_spectrum_analyzer/services/scoring_model_v3.py`
- `data/reference/personalities.csv`
- `data/reference/ideology_taxonomy.csv`
- `data/reference/ideology_aliases.csv`
- `data/reference/profile_coordinate_audit.csv`
- `docs/reference_dataset_profile_audit.md`
- `docs/assets`
- `tests`
- `requirements.txt`
- `pyproject.toml`
- `.streamlit/config.toml`
- `LICENSE`

---

## Screenshots

![Desktop App](docs/assets/desktop-app.png)
![Streamlit Home](docs/assets/streamlit-home.png)
![Streamlit Multi Profile Chart](docs/assets/streamlit-multi-profile-chart.png)
![Streamlit Profile Analysis](docs/assets/streamlit-profile-analysis.png)
![Streamlit Profile Import Export](docs/assets/streamlit-profile-import-export.png)


## Data and privacy

The repository is structured around local CSV reference data and Streamlit profile manipulation. Before public deployment, review file-upload behavior, Streamlit configuration, and hosting settings.

No database-backed profile-storage contract is documented here because no such contract is verified in the repository state used for this README.

---

## Known limitations

- Reference-personality coordinates are analytical approximations.
- Historical and political labels simplify complex positions.
- Two profiles may share a similar graph position while having different internal 16-axis score structures.
- Some coordinate placements may still require manual review; check `data/reference/profile_coordinate_audit.csv` when present.
- The methodology coefficients are explicit and testable, but they remain model choices rather than objective political measurements.

---

## Maintenance checklist

Before a release:

```powershell
python -m pytest
streamlit run streamlit_app.py
```

Review:

- reference dataset size and schema;
- gender metadata values in the sidebar;
- reference filters;
- methodology tab;
- detailed profile analysis;
- coordinate-audit report;
- README accuracy against current files.

---

## License

MIT
