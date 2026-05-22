"""Methodology rendering for the Streamlit app."""

from __future__ import annotations

import streamlit as st

from political_spectrum_analyzer.streamlit_ui.text import translate


METHODOLOGY_V2_MARKDOWN = """## How the analyzer works

The analyzer currently uses **scoring model v2** for x/y positioning.

- **x**: economic position, from economic left to economic right.
- **y**: social-authority position, from libertarian / progressive to authoritarian / conservative.

The model builds weighted ideological blocks, compares opposite blocks, applies secondary adjustments, normalizes each raw axis with `/ 120`, then maps the result into `[-4, 4]` with `sigmoid_scaled`.

---

## 1. Economic blocks

```text
economic_left =
    0.90 * communisme
  + 0.70 * regulation
  + 0.35 * ecologie
  + 0.25 * revolution

economic_right =
    0.90 * capitalisme
  + 0.75 * laissez_faire
  + 0.25 * productivisme
  + 0.20 * reformisme
```

`revolution` and `reformisme` are included in v2 as political-method pressures. This makes the coordinate more sensitive to rupture vs institutional reform than the later v3 experiment.

---

## 2. Societal blocks

```text
social_libertarian =
    0.70 * constructivisme
  + 0.65 * justice_rehabilitative
  + 0.70 * progressisme
  + 0.50 * internationalisme

social_authoritarian =
    0.60 * essentialisme
  + 0.70 * justice_punitive
  + 0.70 * conservatisme
  + 0.50 * nationalisme
```

---

## 3. Raw axis calculation

```text
economic_raw = economic_right - economic_left
social_raw = social_authoritarian - social_libertarian
```

Positive `economic_raw` pushes the profile to the economic right. Positive `social_raw` pushes the profile toward authority / conservatism.

---

## 4. Secondary adjustments

```text
economic_raw += 0.12 * (productivisme - ecologie)
social_raw += 0.10 * (nationalisme - internationalisme)
social_raw += 0.08 * (revolution - reformisme)
```

These adjustments make the coordinate more expressive:

- productivism vs ecology refines the economic direction;
- nationalism vs internationalism refines the societal-authority direction;
- revolution vs reformism adds a strategic-pressure signal to y.

---

## 5. Normalization

```text
economic_normalized = economic_raw / 120
social_normalized = social_raw / 120

x = 4 * sigmoid_scaled(economic_normalized)
y = 4 * sigmoid_scaled(social_normalized)
```

`sigmoid_scaled` keeps the graph bounded and smooth: moderate profiles remain near the center, while strongly marked profiles move toward the edges without leaving the chart.

---

## 6. Meaning of the 16 axes

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

## 7. How to read the result

The graph is a summary. The detailed interpretation is richer because it reads the full 16-axis score set: strongest axes, weakest axes, pair balances, score-by-score notes, strategic tendencies, internal tensions, and profile comparison when several profiles are entered.
"""


METHODOLOGY_V2_MARKDOWN_FR = """## Comment fonctionne l'analyseur

L'analyseur utilise actuellement le **scoring model v2** pour le positionnement x/y.

- **x** : position economique, de la gauche economique vers la droite economique.
- **y** : position societale / autorite, du pole libertaire ou progressiste vers le pole autoritaire ou conservateur.

Le modele construit des blocs ideologiques ponderes, compare les blocs opposes, applique des ajustements secondaires, normalise chaque axe brut avec `/ 120`, puis projette le resultat dans `[-4, 4]` avec `sigmoid_scaled`.

---

## 1. Blocs economiques

```text
economic_left =
    0.90 * communisme
  + 0.70 * regulation
  + 0.35 * ecologie
  + 0.25 * revolution

economic_right =
    0.90 * capitalisme
  + 0.75 * laissez_faire
  + 0.25 * productivisme
  + 0.20 * reformisme
```

`revolution` et `reformisme` sont inclus dans la v2 comme pressions de methode politique. Le positionnement est donc plus sensible a la rupture ou a la reforme institutionnelle.

---

## 2. Blocs societaux

```text
social_libertarian =
    0.70 * constructivisme
  + 0.65 * justice_rehabilitative
  + 0.70 * progressisme
  + 0.50 * internationalisme

social_authoritarian =
    0.60 * essentialisme
  + 0.70 * justice_punitive
  + 0.70 * conservatisme
  + 0.50 * nationalisme
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
economic_raw += 0.12 * (productivisme - ecologie)
social_raw += 0.10 * (nationalisme - internationalisme)
social_raw += 0.08 * (revolution - reformisme)
```

Ces ajustements rendent la coordonnee plus expressive :

- productivisme contre ecologie affine l'axe economique ;
- nationalisme contre internationalisme affine l'axe societal / autorite ;
- revolution contre reformisme ajoute une pression strategique sur y.

---

## 5. Normalisation

```text
economic_normalized = economic_raw / 120
social_normalized = social_raw / 120

x = 4 * sigmoid_scaled(economic_normalized)
y = 4 * sigmoid_scaled(social_normalized)
```

`sigmoid_scaled` garde le graphe borne et progressif : les profils moderes restent proches du centre, tandis que les profils tres marques se rapprochent des bords sans sortir du cadre.

---

## 6. Signification des 16 axes

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

## 7. Comment lire le resultat

Le graphe est un resume. L'interpretation detaillee est plus riche car elle lit les 16 scores : axes forts, axes faibles, equilibres par paires, lecture score par score, strategie politique, tensions internes et comparaison entre profils.
"""


# Backward-compatible names: tests and imports still reference methodology v3 helpers.
METHODOLOGY_V3_MARKDOWN = METHODOLOGY_V2_MARKDOWN
METHODOLOGY_V3_MARKDOWN_FR = METHODOLOGY_V2_MARKDOWN_FR


def render_methodology_v3(language: str | None = None) -> None:
    selected_language = language or "en"
    st.header(translate(selected_language, "tab_methodology"))
    st.markdown(METHODOLOGY_V2_MARKDOWN_FR if selected_language == "fr" else METHODOLOGY_V2_MARKDOWN)
