"""Methodology rendering for the Streamlit app."""

from __future__ import annotations

import streamlit as st

from political_spectrum_analyzer.streamlit_ui.text import translate


METHODOLOGY_V3_MARKDOWN = """## How the analyzer works

The analyzer turns the 16 Politiscales-style scores into two readable coordinates:

- **x**: economic position, from economic left to economic right.
- **y**: social-authority position, from libertarian / progressive to authoritarian / conservative.

The model is not a black box. It builds weighted ideological blocks, compares opposite blocks, applies small secondary adjustments, then normalizes the result into the graph range `[-4, 4]`.

---

## 1. Coordinate system

| Axis | Negative side | Positive side |
|---|---|---|
| `x` economic axis | Economic left | Economic right |
| `y` social-authority axis | Libertarian / progressive | Authoritarian / conservative |

```text
x in [-4, 4]
y in [-4, 4]
```

---

## 2. Score blocks and coefficients

A coefficient is a weight. Higher coefficients have stronger influence on the final coordinate.

### Economic-left block

```text
economic_left =
    0.95 * communisme
  + 0.75 * regulation
  + 0.28 * ecologie
```

- `communisme`: strongest economic-left marker.
- `regulation`: strong interventionist marker.
- `ecologie`: secondary economic-left pressure. Its direct weight is deliberately moderate because ecology can also appear in conservative, localist, or technocratic profiles.

`revolution` is intentionally excluded from this block. It is a method of political change, not an economic doctrine.

### Economic-right block

```text
economic_right =
    0.95 * capitalisme
  + 0.80 * laissez_faire
  + 0.24 * productivisme
```

- `capitalisme`: strongest economic-right marker.
- `laissez_faire`: strong market-autonomy marker.
- `productivisme`: secondary economic-right pressure. Its direct weight is deliberately moderate because productivism can also appear in state-led, socialist, developmentalist, or nationalist profiles.

`reformisme` is intentionally excluded from this block. It is a method of institutional change, not an economic doctrine.

### Libertarian / progressive social block

```text
social_libertarian =
    0.75 * constructivisme
  + 0.70 * justice_rehabilitative
  + 0.75 * progressisme
  + 0.35 * internationalisme
```

- `constructivisme`: strong progressive-social marker.
- `justice_rehabilitative`: strong anti-punitive marker.
- `progressisme`: strong social-change marker.
- `internationalisme`: moderate openness marker, kept below the core social axes because it can also describe institutional or technocratic politics.

### Authoritarian / conservative social block

```text
social_authoritarian =
    0.60 * essentialisme
  + 0.70 * justice_punitive
  + 0.70 * conservatisme
  + 0.30 * nationalisme
```

- `essentialisme`: conservative-social marker.
- `justice_punitive`: authority and sanction marker.
- `conservatisme`: continuity and social-order marker.
- `nationalisme`: moderate sovereignty / national-priority marker, kept below the core authority axes because it can also appear in anti-colonial or democratic-sovereigntist profiles.

---

## 3. Raw axis calculation

```text
economic_raw = economic_right - economic_left
social_raw = social_authoritarian - social_libertarian
```

Interpretation:

- positive `economic_raw` pushes the profile to the economic right;
- negative `economic_raw` pushes it to the economic left;
- positive `social_raw` pushes the profile toward authority / conservatism;
- negative `social_raw` pushes it toward libertarian / progressive positions.

---

## 4. Secondary adjustments

Only two small secondary adjustments are used in the coordinate calculation:

```text
economic_raw += 0.04 * (productivisme - ecologie)
social_raw += 0.03 * (nationalisme - internationalisme)
```

These adjustments are deliberately weak. They refine the reading without making ecology/productivism or nationalism/internationalism dominate the core economic and social blocks.

Removed from coordinate calculation:

```text
revolution - reformisme
```

`revolution` and `reformisme` remain useful for the detailed interpretation, especially to explain the preferred strategy of political change. They do not directly define the economic or social-authority coordinate.

---

## 5. Normalization to `[-4, 4]`

The final coordinates are obtained with hyperbolic tangent normalization:

```text
x = 4 * tanh(0.015 * economic_raw)
y = 4 * tanh(0.015 * social_raw)
```

Why `tanh` is used:

- it keeps the graph bounded between `-4` and `+4`;
- it keeps moderate profiles close to the center;
- it lets strong profiles move toward the edges without exploding out of range;
- it avoids over-compressing all profiles into the same extreme positions.

---

## 6. Role of revolution and reformism

`revolution` and `reformisme` are not discarded. They are used in the **detailed interpretation**:

- rupture vs gradual reform;
- rejection vs correction of institutions;
- radical transformation vs institutional continuity.

They are not direct economic-left/economic-right or libertarian/authoritarian markers.

---

## 7. Meaning of the 16 axes

| Axis | Main meaning |
|---|---|
| `communisme` | collective ownership, anti-capitalist economics |
| `capitalisme` | private property, market-oriented economics |
| `regulation` | state intervention, planning, public constraint |
| `laissez_faire` | market autonomy, deregulation, economic freedom |
| `ecologie` | environmental limits, anti-productivist pressure |
| `productivisme` | growth, production, infrastructure, output |
| `constructivisme` | flexible social interpretation, anti-essentialism |
| `essentialisme` | fixed categories, naturalized social order |
| `justice_rehabilitative` | reintegration, prevention, restorative justice |
| `justice_punitive` | sanction, deterrence, punitive order |
| `progressisme` | social change, equality expansion, reform of norms |
| `conservatisme` | continuity, tradition, institutional stability |
| `internationalisme` | cross-border cooperation, universalist openness |
| `nationalisme` | sovereignty, national priority, cohesion |
| `revolution` | rupture-oriented change strategy |
| `reformisme` | gradual, institutional change strategy |

---

## 8. How to read the result

The app gives several levels of reading:

1. **Graph position**: where the profile appears on the x/y spectrum.
2. **Closest references**: which reference personalities are geometrically closest.
3. **Detailed profile analysis**: strongest axes, weakest axes, pair balances, strategic tendencies, and internal tensions.
4. **Profile comparison**: when several profiles are entered, the app compares their coordinates and their underlying score patterns.

The graph is a summary. The detailed interpretation is richer because it reads the full 16-axis score set.

---

## 9. Methodological limits

This model is an analytical approximation. It is not a scientific diagnosis and should not be treated as a definitive ideological identity.

Important limits:

- coordinates depend on selected coefficients;
- political labels are simplifications;
- historical figures and reference personalities are approximate placements;
- two profiles can share a graph position while having different internal score structures;
- secondary dimensions should be interpreted as nuance, not as absolute classification.
"""


METHODOLOGY_V3_MARKDOWN_FR = """## Comment fonctionne l'analyseur

L'analyseur transforme les 16 scores de type Politiscales en deux coordonnees lisibles :

- **x** : position economique, de la gauche economique vers la droite economique.
- **y** : position societale / autorite, du pole libertaire ou progressiste vers le pole autoritaire ou conservateur.

Le modele n'est pas une boite noire. Il construit des blocs ideologiques ponderes, compare les blocs opposes, applique de petits ajustements secondaires, puis normalise le resultat dans l'intervalle `[-4, 4]`.

---

## 1. Systeme de coordonnees

| Axe | Cote negatif | Cote positif |
|---|---|---|
| `x` axe economique | Gauche economique | Droite economique |
| `y` axe societal / autorite | Libertaire / progressiste | Autoritaire / conservateur |

---

## 2. Blocs de scores et coefficients

Un coefficient est un poids. Plus il est eleve, plus le score influence la coordonnee finale.

### Bloc economique de gauche

```text
economic_left =
    0.95 * communisme
  + 0.75 * regulation
  + 0.28 * ecologie
```

`revolution` est exclu de ce bloc : c'est une strategie de changement politique, pas une doctrine economique.

### Bloc economique de droite

```text
economic_right =
    0.95 * capitalisme
  + 0.80 * laissez_faire
  + 0.24 * productivisme
```

`reformisme` est exclu de ce bloc : c'est une methode de changement institutionnel, pas une doctrine economique.

### Bloc societal libertaire / progressiste

```text
social_libertarian =
    0.75 * constructivisme
  + 0.70 * justice_rehabilitative
  + 0.75 * progressisme
  + 0.35 * internationalisme
```

### Bloc societal autoritaire / conservateur

```text
social_authoritarian =
    0.60 * essentialisme
  + 0.70 * justice_punitive
  + 0.70 * conservatisme
  + 0.30 * nationalisme
```

---

## 3. Calcul brut des axes

```text
economic_raw = economic_right - economic_left
social_raw = social_authoritarian - social_libertarian
```

Un `economic_raw` positif pousse le profil vers la droite economique. Un `social_raw` positif pousse le profil vers le pole autoritaire / conservateur.

---

## 4. Ajustements secondaires

```text
economic_raw += 0.04 * (productivisme - ecologie)
social_raw += 0.03 * (nationalisme - internationalisme)
```

Ces ajustements restent faibles. Ils apportent une nuance sans laisser ecologie/productivisme ou nationalisme/internationalisme dominer les axes centraux.

`revolution` et `reformisme` restent utiles pour l'analyse strategique detaillee, mais ils ne positionnent pas directement le profil en x/y.

---

## 5. Normalisation dans `[-4, 4]`

```text
x = 4 * tanh(0.015 * economic_raw)
y = 4 * tanh(0.015 * social_raw)
```

La fonction `tanh` garde le graphe borne, maintient les profils moderes pres du centre et evite que les profils marques sortent de l'echelle.

---

## 6. Role de revolution et reformisme

`revolution` et `reformisme` servent a expliquer la methode politique preferee :

- rupture ou reforme graduelle ;
- rejet ou correction des institutions ;
- transformation radicale ou continuite institutionnelle.

---

## 7. Signification des 16 axes

| Axe | Sens principal |
|---|---|
| `communisme` | propriete collective, logique anti-capitaliste |
| `capitalisme` | propriete privee, marche, initiative economique |
| `regulation` | intervention publique, regles, correction du marche |
| `laissez_faire` | autonomie du marche, deregulation |
| `ecologie` | limites environnementales, contrainte ecologique |
| `productivisme` | croissance, production, capacite materielle |
| `constructivisme` | lecture flexible du social |
| `essentialisme` | categories fixes, ordre social naturalise |
| `justice_rehabilitative` | reinsertion, prevention, justice reparatrice |
| `justice_punitive` | sanction, dissuasion, ordre punitif |
| `progressisme` | changement social, extension des droits |
| `conservatisme` | continuite, tradition, stabilite institutionnelle |
| `internationalisme` | cooperation internationale, ouverture universaliste |
| `nationalisme` | souverainete, priorite nationale, cohesion |
| `revolution` | strategie de rupture |
| `reformisme` | strategie graduelle et institutionnelle |

---

## 8. Comment lire le resultat

Le graphe est un resume. L'interpretation detaillee est plus riche car elle lit les 16 scores : axes forts, axes faibles, equilibres par paires, strategie politique, tensions internes et comparaison entre profils.
"""


def render_methodology_v3(language: str | None = None) -> None:
    selected_language = language or "en"
    st.header(translate(selected_language, "tab_methodology"))
    st.markdown(METHODOLOGY_V3_MARKDOWN_FR if selected_language == "fr" else METHODOLOGY_V3_MARKDOWN)
