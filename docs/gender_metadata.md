# Gender metadata

The reference dataset includes a normalized `gender` column.

## Purpose

The `gender` field is used for dataset auditing and representational coverage checks. It is not part of the ideological scoring model and must not modify coordinates, interpretation text, or profile comparison logic.

## Allowed values

| Value | Meaning |
|---|---|
| `male` | The reference profile is coded as male. |
| `female` | The reference profile is coded as female. |
| `unknown` | The reference profile cannot be confidently coded or the value is intentionally unspecified. |

## Rules

- Keep values lowercase.
- Do not add free-text variants such as `M`, `F`, `woman`, `man`, or `other`.
- Use `unknown` when the metadata is unclear.
- Do not use gender as an ideological proxy.
- Keep `display_group` as descriptive metadata and `role_category` as the main role filter.
