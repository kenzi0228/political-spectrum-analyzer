# Advanced profile comparison v3

## Objective

The v3 comparison layer makes profile-to-profile comparison more useful and less repetitive.

## What changed

- Adds normalized ideological distance between two profiles.
- Adds an estimated compatibility score.
- Explains convergence on the main axes.
- Explains divergence on the main axes.
- Uses secondary dimensions when available.
- Ranks gaps by importance.

## Compatibility score

The score is derived from x/y distance. It should be read as a rough analytical indicator, not as a scientific compatibility measure.

## Ranked gaps

`ranked_gaps` lists the largest differences first. It can include:

- economic axis;
- social-authority axis;
- secondary dimensions such as ecology, nationalism, internationalism, reformism, or revolution.

## Non-repetition rule

Comparison text must pass through `deduplicate_comparison_sentences` before display.
