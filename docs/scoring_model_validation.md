# Scoring model validation status

## Model

The web application uses `scoring-model-v2.1`. Its blocks, adjustments,
normalization scale, explanations, and UI formula are generated from
`web/model.ts`.

## Evidence status

The model is an editorial heuristic. It has not yet been calibrated against a
representative labeled population and must not be described as a statistical
classifier.

Current automated guarantees cover:

- output bounds;
- neutral-profile centering;
- monotonic movement for isolated model inputs;
- consistency between displayed contributions and projection weights;
- deterministic results for identical scores.

## Validation backlog

- sensitivity analysis for every weight;
- test-retest reliability study;
- inter-rater agreement on reference coordinates;
- comparison with external political-science scales;
- uncertainty intervals around x/y;
- documented benchmark profiles reviewed by multiple evaluators.

Until these studies exist, the UI uses “directional readability” rather than
“confidence” for personalized interpretation.
