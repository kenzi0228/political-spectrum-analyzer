# Methodology

## 1. Purpose of the project

Political Spectrum Analyzer is an exploratory desktop application designed to transform ideological scores into a two-dimensional political projection.

The project is not intended to produce an objective or academically definitive political classification. It provides an explainable heuristic model that helps users:

- visualize ideological positioning;
- compare several profiles;
- identify approximate proximity to reference personalities;
- export profile and reference data for further analysis.

The application is built as a portfolio project combining Python software engineering, data visualization, OCR-assisted import, text parsing, CSV export, and structured reference data management.

---

## 2. Input variables

The application uses 16 Politiscales-inspired variables grouped into ideological oppositions:

| Left-side variable | Right-side variable |
|---|---|
| constructivisme | essentialisme |
| justice_rehabilitative | justice_punitive |
| progressisme | conservatisme |
| internationalisme | nationalisme |
| communisme | capitalisme |
| regulation | laissez_faire |
| ecologie | productivisme |
| revolution | reformisme |

Each variable is expected to be an integer score between 0 and 100.

The scores can be entered manually, imported from copied text, or extracted from a screenshot through OCR.

---

## 3. Projection model

The model projects the 16-dimensional score vector into a 2D coordinate system:

- `x < 0`: economically left;
- `x > 0`: economically right;
- `y < 0`: socially libertarian / progressive;
- `y > 0`: socially authoritarian / conservative.

The current model is heuristic and intentionally transparent. It uses weighted sums to estimate two macro dimensions:

```text
economic_raw = economic_right - economic_left
societal_raw = societal_authoritarian - societal_libertarian
```

The raw differences are then scaled into the plotting range:

```text
x, y in [-4, 4]
```

The purpose is to produce a readable and explainable political map rather than a statistically validated latent-space model.

---

## 4. Economic axis

The economic axis compares left-economic indicators with right-economic indicators.

Typical left-economic contributors include:

- communisme;
- regulation;
- ecologie, with a lighter weight when used as an economic signal.

Typical right-economic contributors include:

- capitalisme;
- laissez_faire;
- productivisme, with a lighter weight when used as an economic signal.

This means that a profile with high regulation and communism scores will move left on the `x` axis, while a profile with high capitalism and laissez-faire scores will move right.

---

## 5. Societal axis

The societal axis compares libertarian/progressive indicators with authoritarian/conservative indicators.

Typical libertarian/progressive contributors include:

- constructivisme;
- justice_rehabilitative;
- progressisme;
- internationalisme.

Typical authoritarian/conservative contributors include:

- essentialisme;
- justice_punitive;
- conservatisme;
- nationalisme.

This means that a profile with high progressivism, constructivism, and rehabilitative justice scores will move downward on the `y` axis, while a profile with high conservatism, nationalism, and punitive justice scores will move upward.

---

## 6. Radicality

The pair `revolution` / `reformisme` is not treated as a primary economic or societal axis.

It is better understood as a political style or radicality dimension:

- high revolution: rupture-oriented or revolutionary posture;
- high reformisme: institutional or gradualist posture.

This dimension may be used in future versions to influence marker size, profile interpretation, or additional analysis panels. It is intentionally not over-weighted in the current 2D projection to avoid confusing ideological direction with political intensity.

---

## 7. Quadrant interpretation

The graph is divided into four broad quadrants:

| Quadrant | Interpretation |
|---|---|
| Left / Authoritarian | economically left and socially authoritarian |
| Right / Authoritarian | economically right and socially authoritarian |
| Left / Libertarian | economically left and socially libertarian |
| Right / Libertarian | economically right and socially libertarian |

Profiles close to the center should be interpreted carefully. A small threshold is used to avoid over-classifying near-center positions.

---

## 8. Reference personalities

The project includes a reference dataset of 150 historical, philosophical, and political figures.

These reference positions are approximate. They are intended to provide context and visual comparison, not definitive political labels.

Each reference personality includes:

- name;
- display group;
- country or countries;
- period;
- broad ideology family;
- x/y coordinates;
- uncertainty ellipse values;
- confidence level;
- notes.

The reference dataset is deliberately marked as estimated.

---

## 9. Uncertainty ellipses

Reference personalities are displayed with uncertainty ellipses.

The ellipse is not a statistical confidence interval. It represents qualitative uncertainty around the approximate placement of a personality.

The fields are:

- `ux`: uncertainty radius on the economic axis;
- `uy`: uncertainty radius on the societal axis;
- `confidence`: qualitative confidence level.

The current confidence levels are:

| Confidence | Meaning |
|---|---|
| high | relatively stable or less controversial placement |
| medium | approximate but reasonably defensible placement |
| low | highly approximate or debated placement |

Low-confidence figures should be interpreted with more caution.

---

## 10. Closest-reference analysis

For each user profile, the application computes the closest reference personalities using Euclidean distance:

```text
distance = sqrt((x_profile - x_reference)^2 + (y_profile - y_reference)^2)
```

The top closest references are shown in the analysis panel.

This does not mean that the profile is politically identical to the reference. It only means that the 2D coordinates are close within this simplified projection.

---

## 11. Import methods

### Manual input

The user can enter all 16 scores manually.

### Copied-text import

The recommended import mode is copied-text import. It is more reliable than OCR because it avoids image recognition errors.

The parser understands the Politiscales pair structure:

```text
Label A
Label B
A%
neutral%
B%
```

The first percentage is assigned to the first label, the last percentage to the second label, and the middle value is ignored when present.

### OCR import

OCR import uses Tesseract through `pytesseract`. It is optional and non-blocking:

- the application can start without OCR dependencies;
- OCR dependencies are loaded only when screenshot import is used;
- OCR output is parsed through the same tested text parser as copied-text import.

OCR results must be reviewed manually.

---

## 12. Export methodology

The application supports CSV export with configurable reference inclusion:

- profiles only;
- profiles with closest references;
- profiles with all references;
- profiles with currently filtered references.

The export includes profile coordinates, quadrant, distance to center, reference names, reference coordinates, and distances.

---

## 13. Limitations

The main limitations are:

- the political projection is heuristic;
- the reference dataset is approximate;
- political ideologies are multidimensional and cannot be fully represented in 2D;
- historical figures may not map cleanly to contemporary political axes;
- OCR reliability depends heavily on screenshot quality;
- the dataset is designed for exploration, not academic classification.

These limitations are explicitly documented to keep the project honest and defensible.

---

## 14. Future methodological improvements

Potential improvements include:

- adding a third dimension for radicality or internationalism;
- adding confidence-weighted nearest-neighbor analysis;
- documenting sources for each personality;
- allowing alternative projection models;
- adding clustering of reference personalities;
- creating a calibration dataset;
- adding interactive sensitivity analysis for the weights;
- separating economic, societal, cultural, and geopolitical axes more clearly.