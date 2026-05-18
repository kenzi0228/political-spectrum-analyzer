# Ideology taxonomy v2

The ideology taxonomy defines broad, filterable ideology families while preserving more precise labels in `ideology_subtype`.

## Why this taxonomy exists

The reference dataset is expected to grow toward 500 profiles. Without a controlled taxonomy, filters become noisy, redundant, and difficult to use.

The taxonomy therefore separates:

```text
ideology_family  = broad family used for filtering
ideology_subtype = precise label used for nuance
```

## Files

```text
data/reference/ideology_taxonomy.csv
data/reference/ideology_aliases.csv
```

## Rules

- Keep `ideology_family` broad and filterable.
- Keep `ideology_subtype` more precise.
- Avoid creating a new family when an existing family is enough.
- Use `aliases` for import, normalization, and future enrichment.
- Use `analysis_guidance` to explain when a family should be used.
- The taxonomy must cover every `ideology_family` used in `personalities.csv`.

## Current families

The current taxonomy includes families such as Liberalism, Conservatism, Socialism, Communism, Social democracy, Anarchism, Libertarianism, Nationalism, Fascism, Republicanism, Centrism, Ecologism, Feminism, Anti-colonialism, Populism, Political religion, Arab nationalism, Technocracy, Monarchism, and Authoritarianism.

## Expansion policy

When new reference profiles are added, the preferred process is:

1. reuse an existing `ideology_family`;
2. add nuance to `ideology_subtype`;
3. add aliases if needed;
4. add a new family only if the profile cannot be classified cleanly.


## Coverage guarantee

The taxonomy must cover every `ideology_family` currently used in `data/reference/personalities.csv`.

When a new family appears in the reference dataset, the taxonomy must be extended in the same commit with:

- a description;
- accepted subtypes;
- aliases;
- analysis guidance.
