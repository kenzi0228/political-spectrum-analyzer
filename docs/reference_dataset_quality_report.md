# Reference dataset quality report

Generated: 2026-05-18 23:16 UTC

## Scope

This report summarizes the current reference dataset used by the Political Spectrum Analyzer.

Current dataset size: **350 profiles**.

## Quality gates

| Gate | Status |
|---|---|
| Dataset readable as CSV | Passed |
| Coordinates convertible to numeric values | Passed |
| Taxonomy coverage checked | Passed |
| Duplicate-name control covered by tests | Passed |
| Country-code diversity tracked | Passed |
| Role-category diversity tracked | Passed |
| Confidence distribution tracked | Passed |

## Summary metrics

| Metric | Value |
|---|---|
| Profiles | 350 |
| Ideology families used | 29 |
| Ideology families in taxonomy | 31 |
| Missing taxonomy families | 0 |
| Country codes represented | 82 |
| Role categories represented | 15 |
| Century buckets represented | 7 |
| Low-confidence share | 15.71% |
| Average uncertainty on x | 0.681 |
| Average uncertainty on y | 0.632 |

## Missing taxonomy families

None

## Ideology family distribution

| Item | Count |
|---|---|
| Socialism | 62 |
| Liberalism | 43 |
| Conservatism | 30 |
| Nationalism | 25 |
| Feminism | 22 |
| Communism | 19 |
| Anti-colonialism | 17 |
| Ecologism | 16 |
| Social democracy | 15 |
| Progressivism | 13 |
| Republicanism | 12 |
| Populism | 11 |
| Other | 10 |
| Political religion | 10 |
| Anarchism | 9 |
| Laborism | 7 |
| Authoritarianism | 6 |
| Centrism | 5 |
| Fascism | 4 |
| Post-structuralism | 3 |


## Role-category distribution

| Item | Count |
|---|---|
| Thinker | 81 |
| Head of state | 62 |
| Activist | 39 |
| Writer | 27 |
| Revolutionary | 26 |
| Head of government | 25 |
| Politician | 25 |
| Political Leader | 21 |
| Authoritarian ruler | 20 |
| Economist | 15 |
| Chancellor | 5 |
| King | 1 |
| Crown Prince | 1 |
| Emperor | 1 |
| Historical Leader | 1 |


## Confidence distribution

| Item | Count |
|---|---|
| medium | 275 |
| low | 55 |
| high | 20 |


## Quadrant distribution

| Item | Count |
|---|---|
| left_libertarian | 179 |
| right_authoritarian | 84 |
| left_authoritarian | 58 |
| right_libertarian | 29 |


## Country-code coverage

| Item | Count |
|---|---|
| USA | 91 |
| GBR | 41 |
| FRA | 39 |
| DEU | 23 |
| ITA | 12 |
| ESP | 11 |
| IND | 11 |
| DZA | 10 |
| RUS | 9 |
| BRA | 8 |
| MEX | 8 |
| EGY | 7 |
| SUN | 5 |
| CHN | 5 |
| UNK | 5 |
| PAK | 5 |
| PSE | 5 |
| AUT | 4 |
| ARG | 4 |
| CUB | 4 |
| GRC | 4 |
| IRN | 4 |
| ZAF | 3 |
| POL | 3 |
| HUN | 3 |
| VEN | 3 |
| TUN | 3 |
| KEN | 3 |
| CAN | 3 |
| COL | 3 |


## Notes for future expansion

The next expansion stages should focus on:

- keeping exact schema v2 compatibility;
- improving coordinate confidence for low-confidence profiles;
- adding more non-Western references without introducing a region column;
- maintaining explicit taxonomy coverage for every `ideology_family`;
- avoiding duplicate names and duplicate CSV header rows;
- documenting any high-uncertainty placements through `ux`, `uy`, and `notes`.
