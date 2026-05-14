# Political Spectrum Analyzer

A Python desktop application for visualizing political profiles on a two-dimensional ideological spectrum, comparing them with reference personalities, importing Politiscales-style results, and exporting structured analysis data.

The project was designed as a portfolio-grade data/software engineering project combining:

- explainable scoring and projection logic;
- desktop UI development with Tkinter;
- data visualization with Matplotlib;
- OCR-assisted import;
- robust copied-text parsing;
- structured reference data;
- nearest-reference analysis;
- configurable CSV exports;
- automated tests;
- modern Python package structure.

---

## 1. Project overview

Political Spectrum Analyzer converts 16 ideological scores into a 2D political position.

The application allows users to:

- manually enter ideological scores;
- import results from copied Politiscales-style text;
- optionally import scores from screenshots using OCR;
- visualize one or several profiles on a political spectrum;
- compare profiles with a curated reference dataset of 150 political, philosophical, and historical figures;
- filter reference personalities by group, country, period, and ideology;
- compute closest reference personalities;
- export analysis results to CSV.

The project is intentionally transparent: the model is heuristic and documented, rather than presented as an objective political truth.

---

## 2. Key features

### Score input

The application supports three input methods:

1. Manual entry of the 16 scores.
2. Copied-text import from Politiscales-style results.
3. Optional OCR import from screenshots.

The copied-text parser supports the Politiscales pair format:

```text
Constructivisme
Essentialisme
7%
26%
67%
```

In this structure:

- the first percentage belongs to the first concept;
- the last percentage belongs to the second concept;
- the middle percentage, if present, is ignored.

### 2D political projection

Profiles are projected onto a two-axis space:

```text
x < 0: economic left
x > 0: economic right
y < 0: libertarian / progressive
y > 0: authoritarian / conservative
```

The graph includes quadrant labels and profile coordinates.

### Reference personalities

The project includes a structured dataset of 150 reference figures with metadata:

- name;
- group;
- country or countries;
- historical period;
- ideology family;
- estimated x/y coordinates;
- uncertainty ellipse values;
- confidence level;
- notes.

Reference personalities are approximate and explicitly marked as estimated.

### Advanced filters

Reference personalities can be filtered by:

- group;
- country;
- period;
- ideology family.

The UI supports two special filter modes:

- `None`: do not display references by default;
- `Any`: display all values for that filter dimension.

### Position analysis

For each profile, the application computes:

- x/y coordinates;
- political quadrant;
- distance to center;
- top closest reference personalities using Euclidean distance.

### CSV export

The CSV export is configurable:

- profiles only;
- profiles with closest references;
- profiles with all references;
- profiles with currently filtered references.

---

## 3. Screenshots

Add screenshots in this section before final portfolio publication.

Recommended files:

```text
docs/assets/main_screen.png
docs/assets/analysis_panel.png
docs/assets/export_dialog.png
```

Example Markdown:

```markdown
![Main interface](docs/assets/main_screen.png)
```

---

## 4. Methodology

The projection model is documented in:

```text
docs/methodology.md
```

The model uses weighted score aggregation to estimate two macro dimensions:

```text
economic_raw = economic_right - economic_left
societal_raw = societal_authoritarian - societal_libertarian
```

The results are scaled to a coordinate range from `-4` to `4`.

The model is best understood as an explainable heuristic. It is designed for exploration, comparison, and visualization, not for academic classification.

---

## 5. Reference dataset

The reference dataset is documented in:

```text
docs/reference_dataset.md
```

The dataset is stored in:

```text
data/reference/personalities.csv
```

The data quality tests verify:

- exactly 150 reference entries;
- unique names;
- valid coordinates;
- positive uncertainty values;
- valid confidence levels;
- required metadata;
- country diversity;
- simplified ideology categories.

Multiple countries are separated with semicolons:

```text
France; Algeria
```

This allows the same personality to appear under multiple country filters.

---

## 6. Technical architecture

```text
political-spectrum-analyzer/
â”œâ”€â”€ data/
â”‚   â””â”€â”€ reference/
â”‚       â””â”€â”€ personalities.csv
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ methodology.md
â”‚   â””â”€â”€ reference_dataset.md
â”œâ”€â”€ outputs/
â”œâ”€â”€ src/
â”‚   â””â”€â”€ political_spectrum_analyzer/
â”‚       â”œâ”€â”€ domain/
â”‚       â”‚   â”œâ”€â”€ models.py
â”‚       â”‚   â””â”€â”€ validation.py
â”‚       â”œâ”€â”€ model/
â”‚       â”‚   â””â”€â”€ transforms.py
â”‚       â”œâ”€â”€ ocr/
â”‚       â”‚   â””â”€â”€ politiscales_ocr.py
â”‚       â”œâ”€â”€ plotting/
â”‚       â”‚   â””â”€â”€ plot_2d.py
â”‚       â”œâ”€â”€ services/
â”‚       â”‚   â”œâ”€â”€ analysis_service.py
â”‚       â”‚   â”œâ”€â”€ export_results_service.py
â”‚       â”‚   â”œâ”€â”€ personalities_service.py
â”‚       â”‚   â”œâ”€â”€ personality_filter_service.py
â”‚       â”‚   â”œâ”€â”€ scoring_service.py
â”‚       â”‚   â””â”€â”€ text_import_service.py
â”‚       â”œâ”€â”€ ui/
â”‚       â”‚   â”œâ”€â”€ app.py
â”‚       â”‚   â”œâ”€â”€ form_frame.py
â”‚       â”‚   â”œâ”€â”€ plot_frame.py
â”‚       â”‚   â””â”€â”€ start_frame.py
â”‚       â”œâ”€â”€ cli.py
â”‚       â”œâ”€â”€ config.py
â”‚       â””â”€â”€ constants.py
â”œâ”€â”€ tests/
â”œâ”€â”€ main.py
â”œâ”€â”€ pyproject.toml
â”œâ”€â”€ pytest.ini
â””â”€â”€ requirements.txt
```

---

## 7. Installation

### 7.1 Clone the repository

```bash
git clone https://github.com/kenzi0228/political-spectrum-analyzer.git
cd political-spectrum-analyzer
```

### 7.2 Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 7.3 Install dependencies

Simple installation:

```powershell
python -m pip install -r requirements.txt
```

Editable installation for development:

```powershell
python -m pip install -e .[dev]
```

---

## 8. Running the application

### Option 1: run from main.py

```powershell
python main.py
```

### Option 2: run as an installed package

After editable installation:

```powershell
political-spectrum-analyzer
```

---

## 9. Running tests

```powershell
python -m pytest
```

The project includes tests for:

- scoring validation;
- transformation logic;
- copied-text parsing;
- profile analysis;
- CSV export;
- reference dataset quality;
- personality filters;
- documentation presence;
- package entry point;
- optional OCR behavior.

---

## 10. OCR setup

OCR is optional.

The application can start without OCR dependencies. OCR dependencies are loaded only when the screenshot import feature is used.

To use OCR:

```powershell
python -m pip install pytesseract pillow
```

On Windows, the native Tesseract executable must also be installed.

Common Windows path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

The application contains a fallback path configuration for this location.

OCR remains heuristic. The copied-text import is recommended when possible.

---

## 11. CSV export

The export dialog supports several modes:

| Mode | Description |
|---|---|
| Profiles only | exports only user profiles and computed analysis |
| Profiles + closest references | exports top N closest reference personalities |
| Profiles + all references | exports all references with computed distances |
| Profiles + current filtered references | exports only references matching active UI filters |

The CSV export is suitable for inspection in Excel, Power BI, or downstream Python analysis.

---

## 12. Limitations

This project has explicit methodological limitations:

- the projection model is heuristic;
- the reference dataset is approximate;
- 2D political visualization cannot fully capture ideology;
- historical figures are difficult to map to contemporary axes;
- reference positions should not be interpreted as definitive;
- OCR quality depends on screenshot clarity;
- confidence ellipses are qualitative, not statistical intervals.

These limitations are documented to keep the project transparent and defensible.

---

## 13. Roadmap

Potential future improvements:

- add a third dimension for radicality or internationalism;
- add radar charts for the 16 raw variables;
- add JSON export;
- add a Streamlit or web version;
- add source references for each personality;
- add interactive weight calibration;
- add clustering of reference personalities;
- add profile history and saved sessions;
- add screenshots and demo GIFs to the README;
- improve UI styling and layout consistency.

---

## 14. Recruiter-oriented value

This project demonstrates:

- Python application architecture;
- separation of concerns between UI, services, domain models, plotting, and data;
- test-driven improvements;
- data quality validation;
- CSV data handling;
- text parsing;
- OCR integration;
- data visualization;
- package structuring with `pyproject.toml`;
- GitHub Actions CI;
- clear documentation of assumptions and limitations.

It is designed to be discussed in interviews as both a technical and product-oriented project.

---

## 15. License

This project is intended to be distributed under the MIT License.

If the repository does not yet contain a `LICENSE` file, it should be added before final publication.