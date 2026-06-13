# Reference dataset governance

## Current status

The reference map contains 500 editorial coordinate estimates. As of
June 13, 2026, the `source` column is empty for all 500 rows. The application
therefore labels these records as unsourced and does not present them as
verified facts.

The `confidence` field is an editorial review priority, not a statistical
confidence interval. Coordinates express an approximate placement for a
specified period and must not be interpreted as a complete description of a
person.

## Acceptance requirements

A reference becomes `sourced` only when its row contains:

- a stable primary or reputable secondary source;
- a note connecting the source to the estimated economic and social position;
- an explicit historical period;
- a reviewer and review date in the audit log;
- an explanation for any coordinate change.

Identity-only links and generic search-result URLs are not sufficient evidence
for an ideological coordinate.

## Review workflow

1. Open an issue identifying the person and period.
2. Provide sources and a short coordinate rationale.
3. Compare the proposal with the scoring model and neighboring references.
4. Record the old and new coordinates in the coordinate audit.
5. Obtain a second review for medium- or high-confidence classification.

Mass coordinate changes inferred from ideology labels are prohibited.

## Known identity collisions resolved

The dataset previously contained two Mitterrand rows and two Ben Bella rows
without distinguishing their historical periods. They are now explicitly
labelled as period-specific estimates. Their coordinates remain unchanged and
their source review remains pending.
