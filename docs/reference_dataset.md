# Reference Dataset Documentation

## 1. File location

The reference dataset is stored in:

```text
data/reference/personalities.csv
```

It contains 150 reference personalities used for visual comparison and nearest-reference analysis.

---

## 2. Purpose

The dataset is used to display approximate reference points on the political spectrum.

It is not a factual ranking system and should not be interpreted as an objective political classification.

The goal is to provide contextual anchors that help users interpret their own coordinates.

---

## 3. Columns

| Column | Description |
|---|---|
| `name` | Name of the reference personality |
| `display_group` | Broad type, such as Philosopher, President, Prime Minister, Dictator, Revolutionary |
| `country` | Country or countries associated with the figure |
| `period` | Main historical period |
| `ideology_family` | Simplified broad ideological family |
| `x` | Economic coordinate, from -4 to 4 |
| `y` | Societal coordinate, from -4 to 4 |
| `ux` | Horizontal uncertainty radius |
| `uy` | Vertical uncertainty radius |
| `confidence` | Qualitative confidence level: high, medium, or low |
| `is_estimated` | Whether the placement is estimated |
| `source` | Reserved for references or citations |
| `notes` | Short explanation or caution note |

---

## 4. Coordinate interpretation

The coordinate system follows this convention:

```text
x < 0: economic left
x > 0: economic right
y < 0: libertarian / progressive
y > 0: authoritarian / conservative
```

The plotting range is:

```text
x in [-4, 4]
y in [-4, 4]
```

---

## 5. Country handling

Multiple countries are separated with a semicolon:

```text
France; Algeria
```

The interface treats this as two filterable countries. A figure listed as `France; Algeria` appears under both `France` and `Algeria`.

---

## 6. Ideology categories

The dataset uses simplified ideology categories to avoid excessive fragmentation.

Examples include:

- Socialism;
- Communism;
- Liberalism;
- Conservatism;
- Nationalism;
- Populism;
- Republicanism;
- Green politics;
- Authoritarianism;
- Fascism;
- Anti-colonialism;
- Economic liberalism.

These categories are intentionally broad. They are used for filtering and exploratory comparison, not for definitive classification.

---

## 7. Confidence levels

The `confidence` column indicates how cautious the user should be when interpreting a reference placement.

| Value | Meaning |
|---|---|
| high | relatively stable placement |
| medium | approximate but reasonably defensible placement |
| low | highly approximate or controversial placement |

The visual uncertainty ellipse scales with confidence.

---

## 8. Data quality rules

The project includes tests to enforce dataset consistency:

- exactly 150 entries;
- unique names;
- coordinates inside the plotting range;
- positive uncertainty values;
- valid confidence levels;
- required metadata present;
- no unsupported country categories specified by project constraints;
- reasonable country diversity;
- simplified ideology diversity.

These tests help prevent silent degradation of the reference dataset.

---

## 9. Limitations

The dataset is heuristic. It should be interpreted as a visualization aid.

Limitations include:

- historical context is simplified;
- ideological categories are broad;
- political positions can evolve over time;
- public figures may be interpreted differently by different sources;
- some placements are necessarily approximate.

Future versions should add explicit sources for each reference personality.