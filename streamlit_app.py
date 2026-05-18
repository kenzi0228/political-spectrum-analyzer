from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_SRC_PATH = Path(__file__).resolve().parent / "src"
if PACKAGE_SRC_PATH.exists() and str(PACKAGE_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC_PATH))

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from political_spectrum_analyzer.config import PERSONALITIES_CSV_PATH
from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.model.transforms import apply_transformations_and_get_coordinates
from political_spectrum_analyzer.services.analysis_service import analyze_profile
from political_spectrum_analyzer.services.export_results_service import build_export_rows
from political_spectrum_analyzer.services.personalities_service import load_personalities
from political_spectrum_analyzer.services.profile_interpretation_service import interpret_profile
from political_spectrum_analyzer.services.advanced_profile_interpretation_service import build_advanced_interpretation_rows, build_advanced_profile_interpretation
from political_spectrum_analyzer.services.profile_comparison_service import build_comparison_rows, build_profile_comparisons
from political_spectrum_analyzer.services.personality_filter_service import (
    NONE_VALUE,
    filter_personalities,
    get_unique_values,
)
from political_spectrum_analyzer.services.text_import_service import extract_scores_from_text
from political_spectrum_analyzer.web.plotly_plot import build_political_spectrum_figure


st.set_page_config(
    page_title="Political Spectrum Analyzer",
    page_icon=":bar_chart:",
    layout="wide",
)


CUSTOM_CSS = """
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

.hero-card {
    padding: 1.4rem 1.6rem;
    border-radius: 18px;
    border: 1px solid rgba(37, 99, 235, 0.16);
    background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%);
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    margin-bottom: 1rem;
}

.hero-title {
    font-size: 2.15rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.35rem;
}

.hero-subtitle {
    font-size: 1.02rem;
    color: #475569;
    line-height: 1.55;
    max-width: 1050px;
}

.feature-pill {
    display: inline-block;
    padding: 0.3rem 0.65rem;
    margin: 0.25rem 0.25rem 0.25rem 0;
    border-radius: 999px;
    background: #dbeafe;
    color: #1e3a8a;
    font-size: 0.82rem;
    font-weight: 600;
}

.warning-box {
    padding: 0.85rem 1rem;
    border-radius: 14px;
    border-left: 4px solid #2563EB;
    background: #eff6ff;
    color: #1e3a8a;
    margin: 1rem 0;
}

.small-muted {
    color: #64748b;
    font-size: 0.9rem;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 0.8rem;
    border-radius: 14px;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
}

/* Make metric cards readable when values are long, especially quadrant labels. */
div[data-testid="stMetric"] {
    min-height: 118px;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.86rem;
    color: #334155;
}

div[data-testid="stMetricValue"] {
    font-size: 1.42rem;
    line-height: 1.15;
    white-space: normal;
    overflow-wrap: anywhere;
    word-break: normal;
}

div[data-testid="stMetricValue"] > div {
    white-space: normal;
    overflow-wrap: anywhere;
    word-break: normal;
}

section[data-testid="stSidebar"] {
    background-color: #f8fafc;
}
</style>
"""



UI_TEXT: dict[str, dict[str, str]] = {
    "en": {
        "language_label": "Language",
        "hero_title": "Political Spectrum Analyzer",
        "hero_subtitle": "Build, compare, and interpret political profiles from 16 ideological scores. Enter one or several profiles, project them on the spectrum, compare them with reference personalities, and get a detailed score-based reading of each profile.",
        "hero_help": "Start by entering a profile manually, importing copied Politiscales-style results, or loading a saved profile JSON. The app then shows the graph position, closest references, and a personalized analysis based on the strongest and weakest axes.",
        "politiscales_title": "Need to take or retake the test?",
        "politiscales_description": "You can open Politiscales in a new browser tab, take the test there, then copy and paste the results into this app.",
        "politiscales_link_label": "Open Politiscales test",
        "tab_input": "Input",
        "tab_guide": "Guide",
        "tab_visualization": "Visualization",
        "tab_reference": "Reference data",
        "tab_methodology": "Methodology",
        "guide_header": "User guide",
        "guide_intro": "Use this workflow to create, compare, save, and export political profiles. Start with one profile, then add more profiles if you want to compare several people or scenarios.",
        "guide_step_1": "Step 1 - Enter scores",
        "guide_step_1_body": "Choose the number of profiles to compare. For each profile, you can type exact values with Manual numeric entry, disable it and use sliders, or paste copied Politiscales-style text and apply detected scores.",
        "guide_step_2": "Step 2 - Read the graph",
        "guide_step_2_body": "Open the Visualization tab to view the profile position, closest reference personalities, detailed profile reading, and axis-by-axis balance.",
        "guide_step_3": "Step 3 - Save or export",
        "guide_step_3_body": "Save each profile individually as JSON, or export the full analysis as CSV for Excel, Power BI, or later comparison.",
        "recommended_workflow": "Recommended workflow",
        "recommended_workflow_body": "- Keep Manual numeric entry enabled for precise values.\\n- Enter one profile first and check the result.\\n- Save that profile as JSON if you want to reuse it later.\\n- Increase the number of profiles if you want comparison.\\n- Use filters only when you want reference personalities visible.\\n- Export the CSV when you want a structured analysis file.",
        "profile_save_import": "Profile save and import",
        "profile_save_import_body": "Profile saving is currently file-based. Each profile can be downloaded as a JSON file and imported again later into any profile form. Once imported, the profile remains editable.",
        "input_mode": "Input mode",
        "input_mode_body": "Manual numeric entry is enabled by default. Keep it enabled when you want exact score values. Disable it when you prefer visual adjustment with sliders.",
        "reference_filters": "Reference filters",
        "reference_filters_body": "Reference personalities are hidden by default. None hides references for a cleaner graph. Any displays references for that filter dimension. A specific value displays only matching references.",
        "methodology_header": "How the analyzer works",
        "methodology_intro": "The analyzer turns 16 ideological scores into a readable political position. Each score contributes to one or more interpretive blocks. Those blocks are then compared to produce the final economic coordinate x and societal coordinate y.",
        "coordinate_system": "1. Coordinate system",
        "score_blocks": "2. Score blocks and coefficients",
        "raw_axis": "3. Raw axis calculation",
        "secondary_adjustments": "4. Secondary adjustments",
        "normalization": "5. Normalization and final coordinates",
        "axes_meaning": "6. Meaning of the 16 axes",
        "read_result": "7. How to read your result",
        "input_header": "Profile input",
        "input_intro": "Add one or several profiles. Choose slider input or exact numeric input from the sidebar. Each profile can be saved and imported independently.",
        "manual_numeric_entry": "Manual numeric entry",
        "manual_numeric_help": "On: type exact values for each axis. Off: adjust scores with sliders.",
        "profile_count_label": "Number of profiles to compare",
        "profile_count_help": "Use up to 8 profiles to keep the chart readable.",
        "import_saved_profile": "Import a saved profile",
        "select_saved_json": "Select a saved profile JSON",
        "load_this_profile": "Load this profile",
        "save_this_profile": "Save this profile",
        "download_profile_json": "Download this profile JSON",
        "copied_text_import": "Import from copied Politiscales-style text",
        "paste_results_text": "Paste copied results text",
        "apply_copied_scores": "Apply copied-text scores to this profile",
        "profile_loaded": "Profile loaded. The fields have been filled and remain editable.",
        "profile_save_caption": "Profile save/import is currently local and file-based. A future authenticated version can store profiles per user account.",
        "profile_comparison_header": "Profile comparison analysis",
        "profile_comparison_intro": "This section compares profiles pair by pair using their map distance and their raw 16-axis scores.",
        "profile_comparison_not_enough": "Add at least two profiles to generate a comparison analysis.",
        "profile_comparison_summary": "Summary",
        "profile_comparison_table": "Comparison table",
        "tab_about": "About / How to use",
        "about_header": "About this analyzer",
        "about_intro": "Political Spectrum Analyzer is an interactive tool for turning political test scores into a readable profile, a graph position, and a comparison against reference personalities.",
        "about_for_users_title": "What you can do here",
        "about_for_users_body": "- Create one or several political profiles.\\n- Compare profiles on the same graph.\\n- Save and import profiles as JSON.\\n- Export structured results as CSV.\\n- Read a detailed interpretation based on the strongest and weakest axes.",
        "about_how_to_use_title": "How to use it",
        "about_how_to_use_body": "- Choose a language.\\n- Enter scores manually, use sliders, or paste copied Politiscales-style results.\\n- Add more profiles if you want comparison.\\n- Open the visualization tab to read the graph and the detailed analysis.\\n- Use filters only when you want to display reference personalities.\\n- Save individual profiles as JSON if you want to reuse them later.",
        "about_score_title": "How to read the result",
        "about_score_body": "The x-axis represents the economic position. The y-axis represents the societal position. The detailed interpretation uses the full 16-axis score set, so it gives more context than the graph alone.",
        "about_privacy_title": "Data and privacy",
        "about_privacy_body": "The app does not require an account. Profile saving is file-based: when you download a JSON profile, it stays on your device. The current web version does not store personal profiles in a database.",
        "about_desktop_title": "Desktop and web versions",
        "about_desktop_body": "The desktop version includes optional OCR for local screenshots. The Streamlit web version is lighter and uses copied-text import instead, which makes online deployment more reliable.",
        "advanced_interpretation_header": "Advanced profile interpretation",
        "advanced_interpretation_intro": "This analysis uses the scoring model v2 secondary dimensions to explain the profile beyond its x/y position.",
        "advanced_interpretation_dominant": "Dominant axes",
        "advanced_interpretation_weak": "Weak axes",
        "advanced_interpretation_secondary": "Secondary dimensions",
        "advanced_interpretation_table": "Advanced interpretation table",
        "formula_main_blocks_intro": "The analyzer does not use a black-box model. It builds four weighted blocks, then compares them.",
        "formula_coefficients_note": "A coefficient is a weight. The higher it is, the more that score influences the final coordinate. 0.90 is direct and strong, 0.75 is strong, 0.55 is moderate, and values around 0.20-0.35 are secondary.",
        "formula_left_block_title": "Economic-left block",
        "formula_left_block_explanation": "- 0.90 * communisme: strongest economic-left marker; it directly pushes x to the left.\\n- 0.75 * regulation: strong interventionist marker; it pushes x to the left.\\n- 0.35 * ecologie: moderate contribution because ecology often implies regulation, without being purely economic.\\n- 0.25 * revolution: secondary contribution because radicality is a method, not a complete economic doctrine.",
        "formula_right_block_title": "Economic-right block",
        "formula_right_block_explanation": "- 0.90 * capitalisme: strongest economic-right marker; it directly pushes x to the right.\\n- 0.75 * laissez_faire: strong market-autonomy marker; it pushes x to the right.\\n- 0.35 * productivisme: moderate contribution because growth and production can exist in several systems.\\n- 0.20 * reformisme: weak secondary contribution because reformism is mainly a political method.",
        "formula_libertarian_block_title": "Libertarian / progressive social block",
        "formula_libertarian_block_explanation": "- 0.75 * constructivisme: strong progressive-social marker because it reflects flexible social interpretation.\\n- 0.70 * justice_rehabilitative: strong anti-punitive marker because it favors reintegration and prevention.\\n- 0.70 * progressisme: strong social-change marker.\\n- 0.55 * internationalisme: moderate openness marker because it moves the profile toward broader cooperation.",
        "formula_authoritarian_block_title": "Authoritarian / conservative social block",
        "formula_authoritarian_block_explanation": "- 0.75 * essentialisme: strong conservative-social marker because it reflects fixed social categories.\\n- 0.70 * justice_punitive: strong authority marker because it emphasizes sanction and deterrence.\\n- 0.70 * conservatisme: strong continuity and stability marker.\\n- 0.55 * nationalisme: moderate authority/community marker because it reinforces sovereignty and national priority.",
        "formula_raw_axis_explanation": "The model subtracts opposite blocks. right_economic - left_economic gives the x direction. authoritarian_social - libertarian_social gives the y direction.",
        "formula_adjustments_explanation": "- productivisme - ecologie refines the growth-versus-ecological-constraint reading.\\n- nationalisme - internationalisme refines the sovereignty-versus-global-openness reading.\\n- revolution - reformisme refines the rupture-versus-institutional-change reading.",
        "formula_normalization_explanation": "The raw scores are divided by 120 and passed through a sigmoid. Strong profiles move toward the edges, but the chart remains readable.",
    },
    "fr": {
        "language_label": "Langue",
        "hero_title": "Political Spectrum Analyzer",
        "hero_subtitle": "Creez, comparez et interpretez des profils politiques a partir de 16 scores ideologiques. Ajoutez un ou plusieurs profils, projetez-les sur le spectre, comparez-les a des personnalites de reference et obtenez une analyse detaillee de chaque profil.",
        "hero_help": "Commencez par saisir un profil manuellement, importer un texte copie depuis Politiscales, ou charger un profil JSON sauvegarde. L'application affiche ensuite la position sur le graphe, les references les plus proches et une analyse personnalisee des axes dominants et faibles.",
        "politiscales_title": "Besoin de faire ou refaire le test ?",
        "politiscales_description": "Vous pouvez ouvrir Politiscales dans un nouvel onglet, faire le test, puis copier-coller les resultats dans cette application.",
        "politiscales_link_label": "Ouvrir le test Politiscales",
        "tab_input": "Saisie",
        "tab_guide": "Guide",
        "tab_visualization": "Visualisation",
        "tab_reference": "Donnees de reference",
        "tab_methodology": "Methodologie",
        "guide_header": "Guide utilisateur",
        "guide_intro": "Utilisez ce parcours pour creer, comparer, sauvegarder et exporter des profils politiques. Commencez avec un seul profil, puis ajoutez-en plusieurs si vous voulez comparer des personnes ou des scenarios.",
        "guide_step_1": "Etape 1 - Saisir les scores",
        "guide_step_1_body": "Choisissez le nombre de profils a comparer. Pour chaque profil, vous pouvez saisir les valeurs exactes, desactiver la saisie numerique pour utiliser les sliders, ou coller un texte Politiscales et appliquer les scores detectes.",
        "guide_step_2": "Etape 2 - Lire le graphe",
        "guide_step_2_body": "Ouvrez l'onglet Visualisation pour voir la position du profil, les references les plus proches, l'analyse detaillee et l'equilibre axe par axe.",
        "guide_step_3": "Etape 3 - Sauvegarder ou exporter",
        "guide_step_3_body": "Sauvegardez chaque profil individuellement en JSON, ou exportez l'analyse complete en CSV pour Excel, Power BI ou une comparaison ulterieure.",
        "recommended_workflow": "Parcours recommande",
        "recommended_workflow_body": "- Gardez la saisie numerique activee pour des valeurs precises.\\n- Saisissez d'abord un profil et verifiez le resultat.\\n- Sauvegardez ce profil en JSON si vous voulez le reutiliser.\\n- Augmentez le nombre de profils si vous voulez comparer.\\n- Utilisez les filtres uniquement si vous voulez afficher les personnalites de reference.\\n- Exportez le CSV lorsque vous voulez un fichier d'analyse structure.",
        "profile_save_import": "Sauvegarde et import de profil",
        "profile_save_import_body": "La sauvegarde est actuellement locale et basee sur des fichiers. Chaque profil peut etre telecharge en JSON puis importe plus tard dans n'importe quel formulaire. Une fois importe, le profil reste modifiable.",
        "input_mode": "Mode de saisie",
        "input_mode_body": "La saisie numerique manuelle est activee par defaut. Gardez-la activee pour saisir des valeurs exactes. Desactivez-la si vous preferez ajuster les scores avec des sliders.",
        "reference_filters": "Filtres de reference",
        "reference_filters_body": "Les personnalites de reference sont masquees par defaut. None masque les references pour garder un graphe lisible. Any affiche les references pour cette dimension. Une valeur precise affiche uniquement les references correspondantes.",
        "methodology_header": "Comment fonctionne l'analyseur",
        "methodology_intro": "L'analyseur transforme 16 scores ideologiques en une position politique lisible. Chaque score contribue a un ou plusieurs blocs d'interpretation. Ces blocs sont ensuite compares pour produire la coordonnee economique x et la coordonnee societale y.",
        "coordinate_system": "1. Systeme de coordonnees",
        "score_blocks": "2. Blocs de scores et coefficients",
        "raw_axis": "3. Calcul brut des axes",
        "secondary_adjustments": "4. Ajustements secondaires",
        "normalization": "5. Normalisation et coordonnees finales",
        "axes_meaning": "6. Signification des 16 axes",
        "read_result": "7. Comment lire le resultat",
        "input_header": "Saisie du profil",
        "input_intro": "Ajoutez un ou plusieurs profils. Choisissez la saisie exacte ou les sliders depuis la barre laterale. Chaque profil peut etre sauvegarde et importe independamment.",
        "manual_numeric_entry": "Saisie numerique manuelle",
        "manual_numeric_help": "Activee : saisir les valeurs exactes. Desactivee : ajuster les scores avec des sliders.",
        "profile_count_label": "Nombre de profils a comparer",
        "profile_count_help": "Utilisez jusqu'a 8 profils pour garder le graphe lisible.",
        "import_saved_profile": "Importer un profil sauvegarde",
        "select_saved_json": "Selectionner un profil JSON sauvegarde",
        "load_this_profile": "Charger ce profil",
        "save_this_profile": "Sauvegarder ce profil",
        "download_profile_json": "Telecharger ce profil JSON",
        "copied_text_import": "Importer depuis un texte Politiscales copie",
        "paste_results_text": "Coller le texte des resultats",
        "apply_copied_scores": "Appliquer les scores detectes a ce profil",
        "profile_loaded": "Profil charge. Les champs ont ete remplis et restent modifiables.",
        "profile_save_caption": "La sauvegarde est actuellement locale et basee sur des fichiers. Une future version authentifiee pourra stocker les profils par compte utilisateur.",
        "profile_comparison_header": "Analyse comparative des profils",
        "profile_comparison_intro": "Cette section compare les profils deux a deux a partir de leur distance sur le graphe et de leurs 16 scores bruts.",
        "profile_comparison_not_enough": "Ajoutez au moins deux profils pour generer une analyse comparative.",
        "profile_comparison_summary": "Resume",
        "profile_comparison_table": "Tableau comparatif",
        "tab_about": "A propos / Mode d emploi",
        "about_header": "A propos de cet analyseur",
        "about_intro": "Political Spectrum Analyzer est un outil interactif qui transforme des scores politiques en profil lisible, en position sur un graphe et en comparaison avec des personnalites de reference.",
        "about_for_users_title": "Ce que vous pouvez faire",
        "about_for_users_body": "- Creer un ou plusieurs profils politiques.\\n- Comparer plusieurs profils sur le meme graphe.\\n- Sauvegarder et importer des profils en JSON.\\n- Exporter les resultats en CSV.\\n- Lire une interpretation detaillee basee sur les axes les plus forts et les plus faibles.",
        "about_how_to_use_title": "Comment l utiliser",
        "about_how_to_use_body": "- Choisissez une langue.\\n- Entrez les scores manuellement, utilisez les sliders ou collez des resultats de type Politiscales.\\n- Ajoutez plusieurs profils si vous voulez comparer.\\n- Ouvrez l onglet Visualisation pour lire le graphe et l analyse detaillee.\\n- Utilisez les filtres uniquement si vous voulez afficher les personnalites de reference.\\n- Sauvegardez les profils individuellement en JSON si vous voulez les reutiliser.",
        "about_score_title": "Comment lire le resultat",
        "about_score_body": "L axe x represente la position economique. L axe y represente la position societale. L interpretation detaillee utilise les 16 scores, ce qui donne plus de contexte que le graphe seul.",
        "about_privacy_title": "Donnees et confidentialite",
        "about_privacy_body": "L application ne demande pas de compte. La sauvegarde est basee sur des fichiers : quand vous telechargez un profil JSON, il reste sur votre appareil. La version web actuelle ne stocke pas les profils personnels dans une base de donnees.",
        "about_desktop_title": "Versions desktop et web",
        "about_desktop_body": "La version desktop inclut un OCR optionnel pour les captures locales. La version web Streamlit est plus legere et utilise plutot l import par texte copie, ce qui rend le deploiement en ligne plus fiable.",
        "advanced_interpretation_header": "Interpretation avancee du profil",
        "advanced_interpretation_intro": "Cette analyse utilise les dimensions secondaires du modele v2 pour expliquer le profil au-dela de sa position x/y.",
        "advanced_interpretation_dominant": "Axes dominants",
        "advanced_interpretation_weak": "Axes faibles",
        "advanced_interpretation_secondary": "Dimensions secondaires",
        "advanced_interpretation_table": "Tableau d interpretation avancee",
        "formula_main_blocks_intro": "L'analyseur n'utilise pas un modele boite noire. Il construit quatre blocs ponderes, puis les compare.",
        "formula_coefficients_note": "Un coefficient est un poids. Plus il est eleve, plus le score influence la coordonnee finale. 0.90 est direct et fort, 0.75 est fort, 0.55 est modere, et les valeurs autour de 0.20-0.35 sont secondaires.",
        "formula_left_block_title": "Bloc economique de gauche",
        "formula_left_block_explanation": "- 0.90 * communisme : marqueur economique de gauche le plus fort ; il pousse directement x vers la gauche.\\n- 0.75 * regulation : marqueur interventionniste fort ; il pousse x vers la gauche.\\n- 0.35 * ecologie : contribution moderee car l'ecologie implique souvent de la regulation, sans etre purement economique.\\n- 0.25 * revolution : contribution secondaire car la radicalite est une methode, pas une doctrine economique complete.",
        "formula_right_block_title": "Bloc economique de droite",
        "formula_right_block_explanation": "- 0.90 * capitalisme : marqueur economique de droite le plus fort ; il pousse directement x vers la droite.\\n- 0.75 * laissez_faire : marqueur fort d'autonomie du marche ; il pousse x vers la droite.\\n- 0.35 * productivisme : contribution moderee car croissance et production peuvent exister dans plusieurs systemes.\\n- 0.20 * reformisme : contribution secondaire faible car le reformisme est surtout une methode politique.",
        "formula_libertarian_block_title": "Bloc societal libertaire / progressiste",
        "formula_libertarian_block_explanation": "- 0.75 * constructivisme : marqueur social progressiste fort car il traduit une lecture flexible du social.\\n- 0.70 * justice_rehabilitative : marqueur anti-punitif fort car il favorise reintegration et prevention.\\n- 0.70 * progressisme : marqueur fort d'ouverture au changement social.\\n- 0.55 * internationalisme : marqueur modere d'ouverture vers une cooperation elargie.",
        "formula_authoritarian_block_title": "Bloc societal autoritaire / conservateur",
        "formula_authoritarian_block_explanation": "- 0.75 * essentialisme : marqueur social conservateur fort car il traduit des categories sociales plus fixes.\\n- 0.70 * justice_punitive : marqueur d'autorite fort car il insiste sur sanction et dissuasion.\\n- 0.70 * conservatisme : marqueur fort de continuite et stabilite.\\n- 0.55 * nationalisme : marqueur modere d'autorite et de communaute car il renforce souverainete et priorite nationale.",
        "formula_raw_axis_explanation": "Le modele soustrait les blocs opposes. right_economic - left_economic donne la direction de x. authoritarian_social - libertarian_social donne la direction de y.",
        "formula_adjustments_explanation": "- productivisme - ecologie affine la lecture croissance contre contrainte ecologique.\\n- nationalisme - internationalisme affine la lecture souverainete contre ouverture internationale.\\n- revolution - reformisme affine la lecture rupture contre changement institutionnel.",
        "formula_normalization_explanation": "Les scores bruts sont divises par 120 puis passes dans une sigmoide. Les profils marques se rapprochent des bords, mais le graphe reste lisible.",
    },
}


def _t(language: str, key: str) -> str:
    return UI_TEXT.get(language, UI_TEXT["en"]).get(key, UI_TEXT["en"].get(key, key))


def _md_text(language: str, key: str) -> str:
    return _t(language, key).replace("\\n", "\n")


def _render_politiscales_link(language: str) -> None:
    st.markdown(
        f"""
        <div class="warning-box">
            <strong>{_t(language, "politiscales_title")}</strong><br>
            {_t(language, "politiscales_description")}<br>
            <a href="https://politiscales.fr/" target="_blank" rel="noopener noreferrer">
                {_t(language, "politiscales_link_label")}
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _format_variable_name(variable_name: str) -> str:
    return variable_name.replace("_", " ").capitalize()


@st.cache_data
def _load_reference_personalities():
    return load_personalities(PERSONALITIES_CSV_PATH)


def _default_scores() -> dict[str, int]:
    return {variable: 0 for variable in VARIABLE_NAMES}


def _profile_state_prefix(profile_index: int) -> str:
    return f"profile_{profile_index}"


def _build_person_result(profile_name: str, scores: dict[str, int]) -> PersonResult:
    x, y = apply_transformations_and_get_coordinates(scores)

    return PersonResult(
        name=profile_name.strip() or "Profile",
        scores=scores,
        x=float(x),
        y=float(y),
    )


def _profile_payload(person: PersonResult) -> dict[str, object]:
    return {
        "schema": "political_spectrum_profile.v1",
        "saved_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "name": person.name,
        "scores": {axis: int(person.scores.get(axis, 0)) for axis in VARIABLE_NAMES},
    }


def _apply_profile_payload_to_state(profile_index: int, payload: dict[str, object]) -> None:
    prefix = _profile_state_prefix(profile_index)
    name = str(payload.get("name", f"Profile {profile_index + 1}"))
    raw_scores = payload.get("scores", {})

    if not isinstance(raw_scores, dict):
        raise ValueError("Invalid profile file: 'scores' must be an object.")

    st.session_state[f"{prefix}_name"] = name

    for axis in VARIABLE_NAMES:
        value = int(raw_scores.get(axis, 0))
        st.session_state[f"{prefix}_{axis}"] = max(0, min(100, value))


def _render_hero(language: str) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">{_t(language, "hero_title")}</div>
            <div class="hero-subtitle">
                {_t(language, "hero_subtitle")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="warning-box">
            {_t(language, "hero_help")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_politiscales_link(language)



def _render_single_profile_analysis(person: PersonResult, personalities) -> None:
    analysis = analyze_profile(person=person, personalities=personalities, top_n=3)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("x coordinate", f"{analysis.x:.3f}")
    col2.metric("y coordinate", f"{analysis.y:.3f}")
    col3.metric("Quadrant", analysis.quadrant)
    col4.metric("Distance to center", f"{analysis.distance_to_center:.3f}")

    closest_data = [
        {
            "Rank": index,
            "Name": match.name,
            "Group": match.display_group,
            "Distance": match.distance,
            "x": match.x,
            "y": match.y,
        }
        for index, match in enumerate(analysis.closest_references, start=1)
    ]

    st.dataframe(pd.DataFrame(closest_data), use_container_width=True, hide_index=True)
    _render_profile_interpretation(person)


def _render_profile_interpretation(person: PersonResult) -> None:
    interpretation = interpret_profile(
        profile_name=person.name,
        scores=person.scores,
    )

    st.markdown("#### Personalized profile reading")
    st.success(interpretation.archetype)
    st.write(interpretation.synthesis)

    reading_col1, reading_col2, reading_col3 = st.columns(3)
    reading_col1.info(interpretation.economic_reading)
    reading_col2.info(interpretation.societal_reading)
    reading_col3.info(interpretation.strategic_reading)

    st.info(interpretation.tension_reading)

    if interpretation.profile_highlights:
        st.markdown("#### Profile highlights")
        for highlight in interpretation.profile_highlights:
            st.markdown(f"- {highlight}")

    dominant_rows = [
        {
            "Axis": axis.label,
            "Score": axis.score,
            "Level": axis.level,
            "Meaning": axis.interpretation,
        }
        for axis in interpretation.dominant_axes
    ]

    weak_rows = [
        {
            "Axis": axis.label,
            "Score": axis.score,
            "Level": axis.level,
            "Meaning": axis.interpretation,
        }
        for axis in interpretation.weak_axes
    ]

    balance_rows = [
        {
            "Dimension": row["dimension"],
            "First pole": row["left_axis"],
            "First score": row["left_score"],
            "Second pole": row["right_axis"],
            "Second score": row["right_score"],
            "Leading tendency": row["leading_side"],
            "Reading": row["reading"],
        }
        for row in interpretation.axis_pair_balances
    ]

    st.markdown("#### Dominant axes")
    st.dataframe(pd.DataFrame(dominant_rows), use_container_width=True, hide_index=True)

    st.markdown("#### Weakest axes")
    st.dataframe(pd.DataFrame(weak_rows), use_container_width=True, hide_index=True)

    st.markdown("#### Axis-by-axis balance")
    st.dataframe(pd.DataFrame(balance_rows), use_container_width=True, hide_index=True)


def _render_analysis(people: list[PersonResult], personalities) -> None:
    if not people:
        st.info("No profile available for analysis.")
        return

    if len(people) == 1:
        st.subheader(f"Analysis - {people[0].name}")
        _render_single_profile_analysis(people[0], personalities)
        return

    st.subheader("Multi-profile analysis")

    summary_rows = []
    for person in people:
        analysis = analyze_profile(person=person, personalities=personalities, top_n=3)
        interpretation = interpret_profile(profile_name=person.name, scores=person.scores)

        closest = analysis.closest_references[0].name if analysis.closest_references else ""

        summary_rows.append(
            {
                "Profile": analysis.name,
                "Profile type": interpretation.archetype,
                "x": analysis.x,
                "y": analysis.y,
                "Quadrant": analysis.quadrant,
                "Distance to center": analysis.distance_to_center,
                "Closest reference": closest,
            }
        )

    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    st.markdown("### Details by profile")
    for person in people:
        with st.expander(person.name, expanded=False):
            _render_single_profile_analysis(person, personalities)


def _render_reference_filters(personalities):
    st.sidebar.header("Controls")
    current_language = st.session_state.get("language", "en")
    st.sidebar.selectbox(
        _t(current_language, "language_label"),
        options=["en", "fr"],
        format_func=lambda value: "English" if value == "en" else "Francais",
        key="language",
    )
    st.sidebar.subheader("Reference filters")

    group = st.sidebar.selectbox(
        "Group",
        get_unique_values(personalities, "display_group"),
        index=0,
        help="None hides references by default. Any displays all values for this dimension.",
    )

    country = st.sidebar.selectbox(
        "Country",
        get_unique_values(personalities, "country"),
        index=0,
    )

    period = st.sidebar.selectbox(
        "Period",
        get_unique_values(personalities, "period"),
        index=0,
    )

    ideology = st.sidebar.selectbox(
        "Ideology",
        get_unique_values(personalities, "ideology_family"),
        index=0,
    )

    filtered = filter_personalities(
        personalities=personalities,
        display_group=group,
        country=country,
        period=period,
        ideology_family=ideology,
    )

    st.sidebar.metric("Displayed references", f"{len(filtered)} / {len(personalities)}")

    if group == NONE_VALUE and country == NONE_VALUE and period == NONE_VALUE and ideology == NONE_VALUE:
        st.sidebar.info("Set one filter to Any or to a specific value to display references.")

    return filtered


def _render_sidebar_export_options():
    st.sidebar.subheader("Export options")

    export_mode = st.sidebar.selectbox(
        "CSV export mode",
        [
            "profiles_only",
            "closest_references",
            "all_references",
            "filtered_references",
        ],
        format_func=lambda value: {
            "profiles_only": "Profiles only",
            "closest_references": "Profiles + closest references",
            "all_references": "Profiles + all references",
            "filtered_references": "Profiles + current filtered references",
        }[value],
    )

    closest_count = st.sidebar.number_input(
        "Closest references count",
        min_value=1,
        max_value=20,
        value=3,
        step=1,
    )

    precise_input_mode = st.sidebar.toggle(
        _t(st.session_state.get("language", "en"), "manual_numeric_entry"),
        value=True,
        help=_t(st.session_state.get("language", "en"), "manual_numeric_help"),
    )

    return export_mode, int(closest_count), precise_input_mode


def _render_score_inputs(
    imported_scores: dict[str, int] | None,
    widget_prefix: str,
    precise_input_mode: bool,
) -> dict[str, int]:
    scores = imported_scores or _default_scores()

    output_scores: dict[str, int] = {}

    categories = {
        "Social and cultural": [
            "constructivisme",
            "essentialisme",
            "progressisme",
            "conservatisme",
        ],
        "Justice and international orientation": [
            "justice_rehabilitative",
            "justice_punitive",
            "internationalisme",
            "nationalisme",
        ],
        "Economic and ecological": [
            "communisme",
            "capitalisme",
            "regulation",
            "laissez_faire",
            "ecologie",
            "productivisme",
        ],
        "Political strategy": [
            "revolution",
            "reformisme",
        ],
    }

    for category, variables in categories.items():
        with st.expander(category, expanded=True):
            cols = st.columns(2)

            for index, variable in enumerate(variables):
                key = f"{widget_prefix}_{variable}"
                if key not in st.session_state:
                    st.session_state[key] = int(scores.get(variable, 0))

                with cols[index % 2]:
                    if precise_input_mode:
                        output_scores[variable] = int(
                            st.number_input(
                                _format_variable_name(variable),
                                min_value=0,
                                max_value=100,
                                step=1,
                                key=key,
                            )
                        )
                    else:
                        output_scores[variable] = int(
                            st.slider(
                                _format_variable_name(variable),
                                min_value=0,
                                max_value=100,
                                step=1,
                                key=key,
                            )
                        )

    for variable in VARIABLE_NAMES:
        output_scores.setdefault(variable, int(scores.get(variable, 0)))

    return output_scores


def _render_profile_import_controls(profile_index: int) -> None:
    prefix = _profile_state_prefix(profile_index)

    if f"{prefix}_upload_nonce" not in st.session_state:
        st.session_state[f"{prefix}_upload_nonce"] = 0

    with st.expander(_t(st.session_state.get("language", "en"), "import_saved_profile"), expanded=False):
        uploaded_file = st.file_uploader(
            _t(st.session_state.get("language", "en"), "select_saved_json"),
            type=["json"],
            key=f"{prefix}_json_upload_{st.session_state[f'{prefix}_upload_nonce']}",
        )

        if uploaded_file is not None:
            if st.button(_t(st.session_state.get("language", "en"), "load_this_profile"), key=f"{prefix}_load_json"):
                try:
                    payload = json.loads(uploaded_file.getvalue().decode("utf-8"))
                    _apply_profile_payload_to_state(profile_index, payload)

                    # Change the uploader key on rerun so the uploaded file is released from the UI.
                    st.session_state[f"{prefix}_upload_nonce"] += 1
                    st.success(_t(st.session_state.get("language", "en"), "profile_loaded"))
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not load this profile file: {exc}")


def _render_profile_import_export(profile_index: int, current_person: PersonResult | None) -> None:
    prefix = _profile_state_prefix(profile_index)

    with st.expander(_t(st.session_state.get("language", "en"), "save_this_profile"), expanded=False):
        if current_person is not None:
            payload = _profile_payload(current_person)
            safe_name = current_person.name.lower().replace(" ", "_").replace("/", "_")

            st.download_button(
                label=_t(st.session_state.get("language", "en"), "download_profile_json"),
                data=json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"),
                file_name=f"{safe_name or 'profile'}_profile.json",
                mime="application/json",
                key=f"{prefix}_download_json",
                use_container_width=True,
            )

            st.caption(
                _t(st.session_state.get("language", "en"), "profile_save_caption")
            )


def _render_profile_input(profile_index: int, precise_input_mode: bool) -> PersonResult:
    widget_prefix = _profile_state_prefix(profile_index)

    st.markdown(f"### Profile {profile_index + 1}")

    _render_profile_import_controls(profile_index)

    if f"{widget_prefix}_name" not in st.session_state:
        st.session_state[f"{widget_prefix}_name"] = f"Profile {profile_index + 1}"

    profile_name = st.text_input(
        "Profile name",
        key=f"{widget_prefix}_name",
    )

    imported_scores = None

    with st.expander(_t(st.session_state.get("language", "en"), "copied_text_import"), expanded=False):
        copied_text = st.text_area(
            _t(st.session_state.get("language", "en"), "paste_results_text"),
            height=200,
            key=f"{widget_prefix}_copied_text",
            placeholder=(
                "Constructivisme\n"
                "Essentialisme\n"
                "7%\n"
                "26%\n"
                "67%"
            ),
        )

        if copied_text.strip():
            imported_scores = extract_scores_from_text(copied_text)
            detected_count = sum(1 for value in imported_scores.values() if value != 0)
            st.success(f"{detected_count}/16 non-zero scores detected from copied text.")

            if st.button(_t(st.session_state.get("language", "en"), "apply_copied_scores"), key=f"{widget_prefix}_apply_text"):
                for axis in VARIABLE_NAMES:
                    st.session_state[f"{widget_prefix}_{axis}"] = int(imported_scores.get(axis, 0))
                st.rerun()

    scores = _render_score_inputs(
        imported_scores=imported_scores,
        widget_prefix=widget_prefix,
        precise_input_mode=precise_input_mode,
    )

    person = _build_person_result(profile_name, scores)
    _render_profile_import_export(profile_index, person)

    return person


def _render_multi_profile_inputs(precise_input_mode: bool) -> list[PersonResult]:
    st.header(_t(st.session_state.get("language", "en"), "input_header"))
    st.markdown('<p class="small-muted">' + _t(st.session_state.get("language", "en"), "input_intro") + '</p>', unsafe_allow_html=True)

    profile_count = st.number_input(
        _t(st.session_state.get("language", "en"), "profile_count_label"),
        min_value=1,
        max_value=8,
        value=1,
        step=1,
        help=_t(st.session_state.get("language", "en"), "profile_count_help"),
    )

    people: list[PersonResult] = []

    if int(profile_count) == 1:
        people.append(_render_profile_input(0, precise_input_mode))
        return people

    tabs = st.tabs([f"Profile {index + 1}" for index in range(int(profile_count))])

    for index, tab in enumerate(tabs):
        with tab:
            people.append(_render_profile_input(index, precise_input_mode))

    return people


def _build_export_dataframe(
    people: list[PersonResult],
    personalities,
    filtered_personalities,
    export_mode: str,
    closest_count: int,
) -> pd.DataFrame:
    rows = build_export_rows(
        people=people,
        personalities=personalities,
        mode=export_mode,
        closest_count=closest_count,
        filtered_personalities=filtered_personalities,
    )

    return pd.DataFrame(rows)


def _render_user_guide_tab(language: str) -> None:
    st.header(_t(language, "guide_header"))

    st.markdown(_md_text(language, "guide_intro"))

    step1, step2, step3 = st.columns(3)

    with step1:
        st.subheader(_t(language, "guide_step_1"))
        st.markdown(_t(language, "guide_step_1_body"))

    with step2:
        st.subheader(_t(language, "guide_step_2"))
        st.markdown(_t(language, "guide_step_2_body"))

    with step3:
        st.subheader(_t(language, "guide_step_3"))
        st.markdown(_t(language, "guide_step_3_body"))

    st.subheader(_t(language, "recommended_workflow"))
    st.markdown(_md_text(language, "recommended_workflow_body"))

    st.subheader(_t(language, "profile_save_import"))
    st.markdown(_md_text(language, "profile_save_import_body"))

    st.subheader(_t(language, "input_mode"))
    st.markdown(_md_text(language, "input_mode_body"))

    st.subheader(_t(language, "reference_filters"))
    st.markdown(_md_text(language, "reference_filters_body"))



def _render_advanced_profile_interpretations(people: list, language: str) -> None:
    st.subheader(_t(language, "advanced_interpretation_header"))
    st.markdown(_t(language, "advanced_interpretation_intro"))

    interpretations = [
        build_advanced_profile_interpretation(person.name, person.scores, person.x, person.y)
        for person in people
    ]

    for interpretation in interpretations:
        with st.expander(interpretation.profile_name, expanded=False):
            st.write(interpretation.short_summary)
            st.markdown(interpretation.detailed_summary)

            metric_cols = st.columns(4)
            metric_cols[0].metric("Coherence", f"{interpretation.coherence_score:.1f}/100")
            metric_cols[1].metric("Intensity", f"{interpretation.intensity_score:.1f}/100")
            metric_cols[2].metric("Moderation", f"{interpretation.moderation_score:.1f}/100")
            metric_cols[3].metric("Radicality", f"{interpretation.radicality_score:.1f}/100")

            st.markdown(f"**{_t(language, 'advanced_interpretation_dominant')}**")
            st.dataframe(pd.DataFrame([axis.__dict__ for axis in interpretation.dominant_axes]), use_container_width=True, hide_index=True)

            st.markdown(f"**{_t(language, 'advanced_interpretation_weak')}**")
            st.dataframe(pd.DataFrame([axis.__dict__ for axis in interpretation.weak_axes]), use_container_width=True, hide_index=True)

            st.markdown(f"**{_t(language, 'advanced_interpretation_secondary')}**")
            st.dataframe(
                pd.DataFrame([{"dimension": key, "value": value} for key, value in interpretation.secondary_dimensions.items()]),
                use_container_width=True,
                hide_index=True,
            )

    st.markdown(f"**{_t(language, 'advanced_interpretation_table')}**")
    st.dataframe(pd.DataFrame(build_advanced_interpretation_rows(interpretations)), use_container_width=True, hide_index=True)


def _render_profile_comparison_analysis(people, language: str) -> None:
    st.subheader(_t(language, "profile_comparison_header"))
    st.markdown(_t(language, "profile_comparison_intro"))

    comparisons = build_profile_comparisons(people)

    if not comparisons:
        st.info(_t(language, "profile_comparison_not_enough"))
        return

    for comparison in comparisons:
        with st.expander(f"{comparison.first_name} vs {comparison.second_name}", expanded=False):
            metric_col_1, metric_col_2 = st.columns(2)
            metric_col_1.metric("Distance", f"{comparison.coordinate_distance:.2f}")
            metric_col_2.metric("Similarity", f"{comparison.ideological_similarity_score:.1f}/100")

            st.markdown(f"**{_t(language, 'profile_comparison_summary')}**")
            st.write(comparison.summary)

            if comparison.shared_strong_axes:
                st.caption("Shared dominant axes: " + ", ".join(comparison.shared_strong_axes))

            if comparison.shared_weak_axes:
                st.caption("Shared weak axes: " + ", ".join(comparison.shared_weak_axes))

            gap_rows = [
                {
                    "axis": gap.axis,
                    "first_score": gap.first_score,
                    "second_score": gap.second_score,
                    "absolute_gap": gap.absolute_gap,
                }
                for gap in comparison.largest_score_gaps
            ]

            st.dataframe(pd.DataFrame(gap_rows), use_container_width=True, hide_index=True)

    st.markdown(f"**{_t(language, 'profile_comparison_table')}**")
    st.dataframe(pd.DataFrame(build_comparison_rows(comparisons)), use_container_width=True, hide_index=True)


def _render_about_tab(language: str) -> None:
    st.header(_t(language, "about_header"))

    st.markdown(_t(language, "about_intro"))

    st.subheader(_t(language, "about_for_users_title"))
    st.markdown(_md_text(language, "about_for_users_body"))

    st.subheader(_t(language, "about_how_to_use_title"))
    st.markdown(_md_text(language, "about_how_to_use_body"))

    st.subheader(_t(language, "about_score_title"))
    st.markdown(_t(language, "about_score_body"))

    st.subheader(_t(language, "about_privacy_title"))
    st.info(_t(language, "about_privacy_body"))

    st.subheader(_t(language, "about_desktop_title"))
    st.markdown(_t(language, "about_desktop_body"))

    _render_politiscales_link(language)



def _render_methodology_tab(language: str) -> None:
    st.header(_t(language, "methodology_header"))

    st.markdown(_t(language, "methodology_intro"))

    st.subheader(_t(language, "coordinate_system"))

    st.markdown(
        """
        | Axis | Negative side | Positive side |
        |---|---|---|
        | `x` economic axis | Economic left | Economic right |
        | `y` societal axis | Libertarian / progressive | Authoritarian / conservative |

        ```text
        x in [-4, 4]
        y in [-4, 4]
        ```
        """
    )

    st.subheader(_t(language, "score_blocks"))

    st.markdown(_md_text(language, "formula_main_blocks_intro"))
    st.info(_md_text(language, "formula_coefficients_note"))

    st.markdown(f"### {_t(language, 'formula_left_block_title')}")
    st.code(
        "left_economic =\\n"
        "    0.90 * communisme\\n"
        "  + 0.75 * regulation\\n"
        "  + 0.35 * ecologie\\n"
        "  + 0.25 * revolution",
        language="text",
    )
    st.markdown(_md_text(language, "formula_left_block_explanation"))

    st.markdown(f"### {_t(language, 'formula_right_block_title')}")
    st.code(
        "right_economic =\\n"
        "    0.90 * capitalisme\\n"
        "  + 0.75 * laissez_faire\\n"
        "  + 0.35 * productivisme\\n"
        "  + 0.20 * reformisme",
        language="text",
    )
    st.markdown(_md_text(language, "formula_right_block_explanation"))

    st.markdown(f"### {_t(language, 'formula_libertarian_block_title')}")
    st.code(
        "libertarian_social =\\n"
        "    0.75 * constructivisme\\n"
        "  + 0.70 * justice_rehabilitative\\n"
        "  + 0.70 * progressisme\\n"
        "  + 0.55 * internationalisme",
        language="text",
    )
    st.markdown(_md_text(language, "formula_libertarian_block_explanation"))

    st.markdown(f"### {_t(language, 'formula_authoritarian_block_title')}")
    st.code(
        "authoritarian_social =\\n"
        "    0.75 * essentialisme\\n"
        "  + 0.70 * justice_punitive\\n"
        "  + 0.70 * conservatisme\\n"
        "  + 0.55 * nationalisme",
        language="text",
    )
    st.markdown(_md_text(language, "formula_authoritarian_block_explanation"))

    st.subheader(_t(language, "raw_axis"))

    st.code(
        "economic_raw = right_economic - left_economic\\n"
        "societal_raw = authoritarian_social - libertarian_social",
        language="text",
    )
    st.markdown(_md_text(language, "formula_raw_axis_explanation"))

    st.subheader(_t(language, "secondary_adjustments"))

    st.code(
        "economic_raw += 0.12 * (productivisme - ecologie)\\n"
        "societal_raw += 0.10 * (nationalisme - internationalisme)\\n"
        "societal_raw += 0.08 * (revolution - reformisme)",
        language="text",
    )
    st.markdown(_md_text(language, "formula_adjustments_explanation"))

    st.subheader(_t(language, "normalization"))

    st.code(
        "economic_normalized = economic_raw / 120\\n"
        "societal_normalized = societal_raw / 120\\n\\n"
        "x = 4 * sigmoid_scaled(economic_normalized)\\n"
        "y = 4 * sigmoid_scaled(societal_normalized)",
        language="text",
    )
    st.markdown(_md_text(language, "formula_normalization_explanation"))

    st.subheader(_t(language, "axes_meaning"))

    axes_rows = [
        {"Axis": "constructivisme", "What it means": "Social norms and identities are understood as shaped by history, institutions, and context.", "High score indicates": "A more constructivist and socially fluid interpretation of society."},
        {"Axis": "essentialisme", "What it means": "Identities, cultures, or social roles are seen as more fixed, inherited, or stable.", "High score indicates": "A stronger attachment to stable social categories and inherited structures."},
        {"Axis": "justice_rehabilitative", "What it means": "Justice is seen through reintegration, prevention, and rehabilitation.", "High score indicates": "Preference for restorative justice and reduced purely punitive logic."},
        {"Axis": "justice_punitive", "What it means": "Justice is seen through sanction, deterrence, responsibility, and order.", "High score indicates": "Preference for stronger penalties and stricter law-and-order responses."},
        {"Axis": "progressisme", "What it means": "Support for social reform, modernization, and expansion of rights.", "High score indicates": "A profile open to social change and progressive reforms."},
        {"Axis": "conservatisme", "What it means": "Attachment to continuity, tradition, social stability, and inherited norms.", "High score indicates": "A profile cautious toward rapid social change."},
        {"Axis": "internationalisme", "What it means": "Preference for cross-border cooperation and global or supranational perspectives.", "High score indicates": "A more cosmopolitan or internationally cooperative outlook."},
        {"Axis": "nationalisme", "What it means": "Priority given to sovereignty, national identity, and national interest.", "High score indicates": "A stronger national-priority and sovereignty-oriented outlook."},
        {"Axis": "communisme", "What it means": "Support for collective ownership, redistribution, or anti-capitalist economic logic.", "High score indicates": "A strong movement toward the economic left."},
        {"Axis": "capitalisme", "What it means": "Support for private ownership, markets, entrepreneurship, and capital accumulation.", "High score indicates": "A strong movement toward the economic right."},
        {"Axis": "regulation", "What it means": "Support for rules, public oversight, and institutional control of markets.", "High score indicates": "A preference for regulated markets and public correction of economic imbalances."},
        {"Axis": "laissez_faire", "What it means": "Support for market autonomy and limited state intervention.", "High score indicates": "A preference for deregulation and freer economic activity."},
        {"Axis": "ecologie", "What it means": "Priority given to environmental responsibility and sustainability.", "High score indicates": "A preference for ecological limits and sustainability over unrestricted growth."},
        {"Axis": "productivisme", "What it means": "Priority given to production, infrastructure, growth, and material expansion.", "High score indicates": "A profile more favorable to output, industry, and productive capacity."},
        {"Axis": "revolution", "What it means": "Preference for rupture, systemic transformation, and radical change.", "High score indicates": "A more rupture-oriented political strategy."},
        {"Axis": "reformisme", "What it means": "Preference for gradual change through existing institutions.", "High score indicates": "A more institutional, gradualist, and reform-oriented strategy."},
    ]

    st.dataframe(pd.DataFrame(axes_rows), use_container_width=True, hide_index=True)

    st.subheader(_t(language, "read_result"))

    st.markdown(
        """
        The app gives three levels of reading:

        1. **Graph position** - where the profile appears on the spectrum.
        2. **Closest references** - which reference personalities are geometrically closest.
        3. **Personalized profile reading** - which axes dominate, which axes are weakest, and which opposing pairs define the profile most strongly.

        The detailed reading is based on the raw 16 scores, not only on the final `x/y` coordinates.
        """
    )



def main() -> None:
    _inject_css()

    personalities = _load_reference_personalities()

    _render_hero(st.session_state.get("language", "en"))

    filtered_personalities = _render_reference_filters(personalities)
    export_mode, closest_count, precise_input_mode = _render_sidebar_export_options()

    language = st.session_state.get("language", "en")

    input_tab, guide_tab, graph_tab, data_tab, methodology_tab = st.tabs(
        [_t(language, "tab_input"), _t(language, "tab_guide"), _t(language, "tab_visualization"), _t(language, "tab_reference"), _t(language, "tab_methodology")]
    )

    with input_tab:
        people = _render_multi_profile_inputs(precise_input_mode)

    with guide_tab:
        _render_user_guide_tab(language)

    with graph_tab:
        st.header("Political positioning")

        fig = build_political_spectrum_figure(
            people=people,
            personalities=filtered_personalities,
        )

        st.plotly_chart(fig, use_container_width=True)

        _render_analysis(people, personalities)

        export_df = _build_export_dataframe(
            people=people,
            personalities=personalities,
            filtered_personalities=filtered_personalities,
            export_mode=export_mode,
            closest_count=closest_count,
        )

        csv_content = export_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Download analysis CSV",
            data=csv_content,
            file_name="political_spectrum_analysis.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with data_tab:
        st.header("Reference dataset")

        data = [
            {
                "Name": person.name,
                "Group": person.display_group,
                "Country": person.country,
                "Period": person.period,
                "Ideology family": person.ideology_family,
                "x": person.x,
                "y": person.y,
                "Confidence": person.confidence,
                "Notes": person.notes,
            }
            for person in personalities
        ]

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    with methodology_tab:
        _render_methodology_tab(language)



    with about_tab:
        _render_about_tab(language)
if __name__ == "__main__":
    main()
# Profile comparison analysis is available through _render_profile_comparison_analysis(people_results, language).


# Intended Streamlit render call: _render_advanced_profile_interpretations(people_results, language)
