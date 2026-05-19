# Reference dataset schema v2

The reference dataset uses a neutral schema designed for controlled expansion beyond 150 personalities.

This version intentionally does not include a `region` field. Geographic macro-regions are avoided because they can be arbitrary, politically loaded, and historically unstable.

## Main file

```text
data/reference/personalities.csv
```

## Required columns

| Column | Meaning |
|---|---|
| `name` | Reference personality name. |
| `display_group` | Public grouping used in graph display. |
| `country` | One or several countries, separated with `;` when needed. |
| `country_codes` | Country codes separated with `;` when several countries apply. |
| `period` | Historical period, such as `20th century` or `20th-21st century`. |
| `century` | Normalized century field used for filtering and quality checks. |
| `ideology_family` | Generalized ideology family for filtering. |
| `ideology_subtype` | More precise original ideology label. |
| `role_category` | General role category such as Thinker, Head of state, Economist, Activist, or Revolutionary. |
| `x` | Economic coordinate. |
| `y` | Societal / authority coordinate. |
| `ux` | X uncertainty. |
| `uy` | Y uncertainty. |
| `confidence` | Confidence level: `low`, `medium`, or `high`. |
| `is_estimated` | Whether the placement is estimated. |
| `source` | Optional source reference. |
| `notes` | Qualitative placement note. |
| `tags` | Semicolon-separated helper tags for search and display. |

## Supporting files

```text
data/reference/ideology_taxonomy.csv
data/reference/reference_sources.csv
```

## Design principles

- The dataset expansion stage now targets 425 reference profiles.
- Avoid a `region` field to keep the schema neutral.
- Use `country` and `country_codes` for geographic filtering.
- Keep ideology families general enough for filtering.
- Keep ideology subtypes precise enough for nuance.
- Use semicolon-separated multi-values for countries, country codes, and tags.
- Treat all placements as approximate political references, not objective labels.

## Expansion target

```text
425 profiles
425 profiles
425 profiles
500 profiles
```

Each expansion step should preserve quality tests for geography, period, ideology diversity, confidence, and coordinate bounds.


## Dataset expansion to 425 profiles

The reference dataset has been expanded from 150 to 425 profiles while preserving schema v2 and quality-gate consistency.


## Gender metadata

The reference dataset includes a `gender` column with normalized values `male`, `female`, or `unknown`. It is used for dataset auditing and optional future UI filtering.
