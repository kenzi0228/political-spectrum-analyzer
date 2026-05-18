# Methodology

## 1. Purpose of the project

Political Spectrum Analyzer is an exploratory application that converts ideological scores into a two-dimensional political projection.

The objective is not to produce an absolute political truth. The objective is to provide a transparent, explainable, and reproducible way to:

- enter or import ideological scores;
- project profiles into a common political space;
- compare several profiles;
- display approximate reference personalities;
- compute nearest reference personalities;
- export structured results for further analysis.

The project should be understood as a portfolio-grade data and software engineering project. It combines a tested scoring pipeline, a curated reference dataset, a desktop interface, a Streamlit web interface, CSV export, and methodological documentation.

---

## 2. Input score system

The model uses 16 input variables inspired by Politiscales-style ideological axes.

Each variable is represented by a score between `0` and `100`.

The variables are organized into conceptual pairs:

| Pair | First pole | Second pole | Interpretation |
|---|---|---|---|
| 1 | constructivisme | essentialisme | social construction vs fixed social/natural categories |
| 2 | justice_rehabilitative | justice_punitive | rehabilitation-oriented justice vs punishment-oriented justice |
| 3 | progressisme | conservatisme | progressive social change vs preservation of traditional norms |
| 4 | internationalisme | nationalisme | international orientation vs national-priority orientation |
| 5 | communisme | capitalisme | collective/socialized economic orientation vs market/private-capital orientation |
| 6 | regulation | laissez_faire | state regulation vs deregulated market approach |
| 7 | ecologie | productivisme | ecological priority vs production/growth priority |
| 8 | revolution | reformisme | rupture-oriented change vs gradual institutional change |

The application supports three input modes in the desktop version:

- manual input;
- copied-text import;
- OCR screenshot import.

The web version supports:

- manual input;
- copied-text import.

OCR is intentionally excluded from the web version because it depends on native Tesseract binaries, which can make free hosting deployments fragile.

---

## 3. Why reduce 16 variables to 2 dimensions?

Political ideology is multidimensional. A 2D projection is necessarily a simplification.

The purpose of the projection is to create a readable map with two widely understood macro dimensions:

1. Economic orientation.
2. Societal / authority orientation.

The reduction is useful because it provides a clear visual representation, but it loses information. For example:

- two profiles can have similar `x/y` coordinates but differ strongly on ecology or revolution;
- radicality is not fully represented by the two axes;
- geopolitical positions are only partially captured through internationalism/nationalism.

The application therefore keeps the raw scores available internally and documents the model limitations explicitly.

---

## 4. Coordinate system

The graph uses the following coordinate system:

```text
x < 0: economic left
x > 0: economic right
y < 0: libertarian / progressive
y > 0: authoritarian / conservative
```

The visible plotting range is:

```text
x in [-4, 4]
y in [-4, 4]
```

The quadrants are interpreted as:

| Quadrant | Meaning |
|---|---|
| Left / Authoritarian | economically left and socially authoritarian |
| Right / Authoritarian | economically right and socially authoritarian |
| Left / Libertarian | economically left and socially libertarian |
| Right / Libertarian | economically right and socially libertarian |
| Center / Moderate | close to the center on both axes |

Profiles near the center should be interpreted cautiously. A near-center result can mean moderation, internal balance, or cancellation between contradictory scores.

---

## 5. Economic axis construction

The economic axis compares an estimated left-economic score against an estimated right-economic score.

Left-economic contributors include:

- `communisme`;
- `regulation`;
- `ecologie`, with a lower weight because ecology is not purely economic;
- `revolution`, with a lower weight because radicality is not equivalent to economic leftism.

Right-economic contributors include:

- `capitalisme`;
- `laissez_faire`;
- `productivisme`, with a lower weight because productivism can exist in different economic systems;
- `reformisme`, with a lower weight because gradualism is not necessarily right-wing.

Conceptually:

```text
economic_raw = right_economic - left_economic
```

If `economic_raw` is negative, the profile moves left.  
If `economic_raw` is positive, the profile moves right.

---

## 6. Societal axis construction

The societal axis compares libertarian/progressive contributors against authoritarian/conservative contributors.

Libertarian/progressive contributors include:

- `constructivisme`;
- `justice_rehabilitative`;
- `progressisme`;
- `internationalisme`.

Authoritarian/conservative contributors include:

- `essentialisme`;
- `justice_punitive`;
- `conservatisme`;
- `nationalisme`.

Conceptually:

```text
societal_raw = authoritarian_social - libertarian_social
```

If `societal_raw` is negative, the profile moves downward toward the libertarian/progressive side.  
If `societal_raw` is positive, the profile moves upward toward the authoritarian/conservative side.

---

## 7. Weighting philosophy

The model uses weighted sums rather than machine learning.

This design choice is intentional:

- the model remains explainable;
- each input has a visible conceptual role;
- the behavior can be discussed and adjusted;
- the project avoids pretending to learn from a dataset that does not exist.

Weights are heuristic. They reflect conceptual importance, not statistical coefficients.

A production-grade or research-grade version would require:

- a labeled calibration dataset;
- expert validation;
- sensitivity analysis;
- uncertainty estimation;
- possibly a higher-dimensional model.

---

## 8. Normalization and bounding

After computing raw economic and societal differences, the model normalizes and compresses the values into the plotting range.

The objective is to avoid extreme jumps and keep all profiles readable on the same chart.

The final coordinates are clamped to:

```text
[-4, 4]
```

This means very extreme profiles are still displayed within the visible graph area.

---

## 9. Radicality and reformism

The `revolution` / `reformisme` pair is difficult to represent on a 2D economic/societal map.

It mostly describes political strategy:

- revolution: rupture, systemic change, radical transformation;
- reformism: gradual change through existing institutions.

This does not map cleanly to left/right or libertarian/authoritarian.

For this reason, the pair has limited influence in the current model. A future version could represent radicality as:

- a third axis;
- marker size;
- color intensity;
- a separate radar chart;
- a dedicated analysis metric.

---

## 10. Multi-profile comparison

The Streamlit version supports several user profiles at once.

Each profile is processed independently:

1. collect 16 scores;
2. compute `x/y`;
3. classify the quadrant;
4. compute distance to center;
5. compute closest references.

The visualization then overlays all user profiles on the same Plotly chart. This enables comparison between individuals, test scenarios, or ideological profiles.

The CSV export also supports multiple profiles and outputs one block of rows per profile.

---

## 11. Reference personality dataset

The application includes a reference dataset of 150 personalities.

Each row includes:

- `name`;
- `display_group`;
- `country`;
- `period`;
- `ideology_family`;
- `x`;
- `y`;
- `ux`;
- `uy`;
- `confidence`;
- `is_estimated`;
- `source`;
- `notes`.

The reference dataset is used for:

- graph overlays;
- filtering;
- closest-reference analysis;
- CSV export.

The dataset is not a ground truth. It is an interpretive reference layer.

---

## 12. Country and ideology metadata

Countries are filterable metadata. If a figure is associated with more than one country, countries are separated by a semicolon:

```text
France; Algeria
```

The filter service treats this as two separate values.

Ideology families are intentionally simplified. The goal is to avoid hundreds of micro-categories that would make filtering unusable.

Examples of broad categories:

- Socialism;
- Communism;
- Liberalism;
- Conservatism;
- Nationalism;
- Populism;
- Republicanism;
- Green politics;
- Authoritarianism;
- Anti-colonialism;
- Economic liberalism;
- Fascism.

---

## 13. Uncertainty ellipses

Reference personalities are displayed with uncertainty values:

- `ux`: horizontal uncertainty radius;
- `uy`: vertical uncertainty radius.

These values are not statistical confidence intervals. They represent qualitative uncertainty in a simplified 2D ideological map.

A larger ellipse means the placement should be interpreted more cautiously.

---

## 14. Confidence levels

Each reference personality has a confidence level:

| Confidence | Meaning |
|---|---|
| high | relatively stable placement |
| medium | approximate but reasonably defensible placement |
| low | highly approximate, contested, or difficult to map |

Confidence influences visual interpretation. Low-confidence figures should not be used as precise anchors.

---

## 15. Closest-reference analysis

Closest references are computed using Euclidean distance in the 2D space:

```text
distance = sqrt((x_profile - x_reference)^2 + (y_profile - y_reference)^2)
```

This is simple and transparent.

However, closeness does not mean ideological identity. It means proximity within this specific reduced 2D model.

Two profiles can be close on the chart while still differing on raw dimensions not fully captured by the projection.

---

## 16. Import methodology

### Manual input

Manual input is the most explicit method. The user directly controls all 16 scores.

### Copied-text import

Copied-text import is the recommended import mode for the web version.

The parser supports patterns where labels and percentages appear as pairs:

```text
Constructivisme
Essentialisme
7%
26%
67%
```

The first percentage is assigned to the first label.  
The last percentage is assigned to the second label.  
The middle percentage, when present, is ignored.

### OCR import

OCR exists in the desktop version only.

It is optional and non-blocking:

- the app can start without OCR dependencies;
- OCR dependencies are loaded only when screenshot import is used;
- OCR output is parsed through the same text parser.

OCR should always be manually reviewed because screenshot quality and Tesseract recognition can introduce errors.

---

## 17. Export methodology

The application supports configurable CSV exports.

Available modes:

| Mode | Meaning |
|---|---|
| profiles only | export only computed profile analysis |
| closest references | export each profile with top N closest references |
| all references | export every reference with distances |
| filtered references | export only the currently displayed reference set |

In the multi-profile web workflow, exports include all entered profiles.

---

## 18. Testing methodology

The project includes tests for:

- scoring validation;
- transformation logic;
- copied-text parsing;
- optional OCR import behavior;
- profile analysis;
- CSV export;
- personality filters;
- dataset quality;
- documentation presence;
- package entry point;
- Plotly figure generation;
- Streamlit deployment documentation.

Dataset quality tests enforce:

- exactly 150 entries;
- unique names;
- valid coordinates;
- valid confidence values;
- required metadata;
- country diversity;
- simplified ideology categories.

---

## 19. Limitations

The main limitations are:

- the projection is heuristic;
- the dataset is approximate;
- historical figures do not map perfectly to modern ideological axes;
- 2D visualization loses information;
- nearest reference does not imply political equivalence;
- OCR can be unreliable;
- confidence ellipses are qualitative, not statistical;
- the model has not been calibrated on a labeled dataset.

These limitations are part of the project design and are documented explicitly to avoid overstating the model.

---

## 20. Future improvements

Potential improvements include:

- adding radar charts for all 16 raw variables;
- adding a third dimension for radicality;
- adding source references for each personality;
- supporting alternative weighting models;
- adding sensitivity analysis;
- adding user profile persistence;
- adding JSON export;
- adding clustering of reference personalities;
- adding a full web deployment URL;
- improving the UI with more advanced visual components.


## Scoring model v2

The revised positioning model separates ideological coordinates from the method of political change.

`revolution` and `reformisme` are not included in the x/y projection anymore. They describe how political change is pursued, not whether a profile is economically left/right or socially authoritarian/libertarian.

They are preserved as a secondary analytical dimension:

```text
change_method = revolution - reformisme
```

Economic coordinate:

```text
economic_left = communisme * 0.95 + regulation * 0.75 + ecologie * 0.38
economic_right = capitalisme * 0.95 + laissez_faire * 0.80 + productivisme * 0.32
x_raw = economic_right - economic_left
x_raw += 0.10 * (productivisme - ecologie)
```

Societal coordinate:

```text
social_libertarian = constructivisme * 0.75 + justice_rehabilitative * 0.70 + progressisme * 0.75 + internationalisme * 0.45
social_authoritarian = essentialisme * 0.65 + justice_punitive * 0.75 + conservatisme * 0.75 + nationalisme * 0.45
y_raw = social_authoritarian - social_libertarian
y_raw += 0.06 * (nationalisme - internationalisme)
```

Saturation:

```text
x = tanh(0.016 * x_raw) * 4
y = tanh(0.016 * y_raw) * 4
```

This keeps moderate profiles nuanced and prevents extreme raw scores from leaving the graph range.


## Advanced interpretation v2

The advanced interpretation uses the scoring model v2 secondary dimensions.

It adds:

- coherence score;
- intensity score;
- moderation score;
- radicality score;
- dominant axes;
- weak axes;
- secondary dimensions such as `change_method`, `globalism_balance`, `justice_balance`, `eco_productivism_balance`, and `social_change_balance`.

Unlike the graph position, this interpretation does not reduce the profile to x/y coordinates. It uses the full score vector to explain why a profile appears where it does and which ideological tensions define it.
