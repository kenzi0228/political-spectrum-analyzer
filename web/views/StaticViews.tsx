import { CircleHelp, SlidersHorizontal } from "lucide-react";
import { MODEL_ADJUSTMENTS, MODEL_BLOCKS, MODEL_STATUS, SCORING_MODEL_VERSION } from "../model";
import type { Language, ViewKey } from "../types";
import { PageHeading } from "../components/Common";

export function HomeView({
  language,
  onNavigate,
}: {
  language: Language;
  onNavigate: (view: ViewKey) => void;
}) {
  return (
    <>
      <section className="home-hero">
        <div className="home-kicker">Politiscales Analyser</div>
        <h1>
          {language === "fr"
            ? "Construisez, comparez et interprétez vos profils politiques."
            : "Build, compare, and interpret political profiles."}
        </h1>
        <p>
          {language === "fr"
            ? "Transformez 16 scores idéologiques en position x/y, comparez plusieurs profils et examinez chaque conclusion jusqu’aux contributions du modèle."
            : "Turn 16 ideological scores into an x/y position, compare profiles, and inspect each conclusion down to its model contributions."}
        </p>
        <div className="feature-pills">
          <span>16 axes</span>
          <span>500 {language === "fr" ? "références estimées" : "estimated references"}</span>
          <span>{language === "fr" ? "Analyse explicable" : "Explainable analysis"}</span>
          <span>{language === "fr" ? "Profils stockés localement" : "Locally stored profiles"}</span>
        </div>
        <div className="home-actions">
          <button className="primary-action" onClick={() => onNavigate("input")}>
            <SlidersHorizontal size={18} />
            {language === "fr" ? "Créer un profil" : "Create a profile"}
          </button>
          <button className="ghost-action" onClick={() => onNavigate("guide")}>
            <CircleHelp size={18} />
            {language === "fr" ? "Consulter le guide" : "Open the guide"}
          </button>
        </div>
      </section>
      <div className="home-grid">
        {[
          ["01", language === "fr" ? "Saisir" : "Input", language === "fr" ? "Importez un profil ou ajustez précisément ses 16 scores." : "Import a profile or precisely adjust all 16 scores."],
          ["02", language === "fr" ? "Visualiser" : "Visualize", language === "fr" ? "Explorez la carte, les filtres et la proximité géométrique des références." : "Explore the map, filters, and geometric proximity of references."],
          ["03", language === "fr" ? "Interpréter" : "Interpret", language === "fr" ? "Distinguez résultats du modèle, tensions et limites de l’interprétation." : "Separate model results, tensions, and interpretation limits."],
        ].map(([number, title, body]) => (
          <section className="home-panel" key={number}>
            <span className="panel-index">{number}</span>
            <h2>{title}</h2>
            <p>{body}</p>
          </section>
        ))}
      </div>
      <section className="privacy-notice">
        <div>
          <strong>{language === "fr" ? "Données et confidentialité" : "Data and privacy"}</strong>
          <p>
            {language === "fr"
              ? "Les profils restent dans le navigateur. Les services publicitaires tiers ne sont chargés qu’après votre choix."
              : "Profiles remain in the browser. Third-party advertising services load only after your choice."}
          </p>
        </div>
      </section>
    </>
  );
}

export function GuideView({ language }: { language: Language }) {
  const steps = language === "fr"
    ? [
        ["1", "Saisissez les scores", "Créez ou importez un profil, puis ajustez les 16 axes."],
        ["2", "Lisez la carte", "Sans filtre, les 500 références estimées sont affichées. Un filtre limite à la fois la carte et les proximités."],
        ["3", "Vérifiez l’analyse", "Consultez les contributions x/y et les contre-signaux avant de retenir une étiquette."],
      ]
    : [
        ["1", "Enter scores", "Create or import a profile, then adjust all 16 axes."],
        ["2", "Read the map", "Without filters, all 500 estimated references are displayed. Filters affect both map and proximity."],
        ["3", "Verify the analysis", "Inspect x/y contributions and counter-signals before accepting a label."],
      ];
  return (
    <>
      <PageHeading
        title={language === "fr" ? "Guide utilisateur" : "User guide"}
        description={language === "fr" ? "Un parcours court pour utiliser le site sans surinterpréter sa projection." : "A short workflow for using the site without overinterpreting its projection."}
      />
      <div className="guide-steps">
        {steps.map(([number, title, body]) => (
          <section className="guide-step" key={number}>
            <span>{number}</span><h2>{title}</h2><p>{body}</p>
          </section>
        ))}
      </div>
      <section className="analysis-block">
        <h2>{language === "fr" ? "Règles de lecture" : "Reading rules"}</h2>
        <ul>
          <li>{language === "fr" ? "La carte synthétise le profil ; elle ne remplace pas les 16 scores." : "The map summarizes a profile; it does not replace the 16 scores."}</li>
          <li>{language === "fr" ? "Une personnalité proche est une proximité géométrique avec une estimation documentaire, pas une identité politique." : "A nearby personality is a geometric proximity to a documentary estimate, not political identity."}</li>
          <li>{language === "fr" ? "Les références sans source sont explicitement signalées comme non vérifiées." : "References without a source are explicitly marked as unverified."}</li>
        </ul>
      </section>
    </>
  );
}

const blockFormula = (name: keyof typeof MODEL_BLOCKS) =>
  `${name} =\n${MODEL_BLOCKS[name]
    .map(({ axis, weight }, index) => `  ${index ? "+ " : ""}${weight.toFixed(2)} * ${axis}`)
    .join("\n")}`;

export function MethodologyView({ language }: { language: Language }) {
  return (
    <>
      <PageHeading
        title={language === "fr" ? "Méthodologie" : "Methodology"}
        description={`${SCORING_MODEL_VERSION} · ${language === "fr" ? "modèle heuristique éditorial, non calibré statistiquement" : "editorial heuristic model, not statistically calibrated"}`}
      />
      <section className="methodology">
        <h2>{language === "fr" ? "Statut du modèle" : "Model status"}</h2>
        <p>
          {language === "fr"
            ? "Les poids sont des choix éditoriaux versionnés. Ils n’expriment ni probabilités ni certitudes scientifiques. La projection sert à explorer un profil et doit être confrontée aux 16 axes."
            : "Weights are versioned editorial choices. They are neither probabilities nor scientific certainty. The projection supports exploration and must be read alongside all 16 axes."}
        </p>
        <div className="formula-grid">
          {(Object.keys(MODEL_BLOCKS) as (keyof typeof MODEL_BLOCKS)[]).map((name) => (
            <pre key={name}>{blockFormula(name)}</pre>
          ))}
        </div>
        <pre>{MODEL_ADJUSTMENTS.map(({ target, positive, negative, weight }) => `${target}_raw += ${weight.toFixed(2)} * (${positive} - ${negative})`).join("\n")}{`\n\nx = 4 * sigmoid_scaled(x_raw / 120)\ny = 4 * sigmoid_scaled(y_raw / 120)`}</pre>
        <h2>{language === "fr" ? "Validation et limites" : "Validation and limitations"}</h2>
        <p>
          {language === "fr"
            ? `Statut actuel : ${MODEL_STATUS.validation}. La sensibilité, la stabilité test-retest et l’accord entre évaluateurs restent à mesurer.`
            : `Current status: ${MODEL_STATUS.validation}. Sensitivity, test-retest stability, and inter-rater agreement remain to be measured.`}
        </p>
      </section>
    </>
  );
}

export function AboutView({ language }: { language: Language }) {
  return (
    <>
      <PageHeading title={language === "fr" ? "À propos" : "About"} description={language === "fr" ? "Positionnement éditorial et responsabilités du projet." : "Editorial position and project responsibilities."} />
      <section className="methodology">
        <h2>Politiscales Analyser</h2>
        <p>{language === "fr" ? "Cet outil indépendant transforme des scores Politiscales en visualisations et lectures heuristiques. Il n’est affilié à aucun parti, candidat ou institution." : "This independent tool turns Politiscales scores into visualizations and heuristic readings. It is not affiliated with any party, candidate, or institution."}</p>
        <p>{language === "fr" ? "Les erreurs de données peuvent être signalées sur le dépôt GitHub, avec des sources et une justification reproductible." : "Data errors can be reported on GitHub with sources and a reproducible rationale."}</p>
      </section>
    </>
  );
}

export function PrivacyView({ language }: { language: Language }) {
  return (
    <>
      <PageHeading title={language === "fr" ? "Politique de confidentialité" : "Privacy policy"} description={language === "fr" ? "Dernière mise à jour : 13 juin 2026." : "Last updated: June 13, 2026."} />
      <section className="legal-copy">
        <h2>{language === "fr" ? "Profils politiques" : "Political profiles"}</h2>
        <p>{language === "fr" ? "Les profils, noms et scores sont enregistrés dans le stockage local de votre navigateur. Ils ne sont pas envoyés à un serveur applicatif par Politiscales Analyser." : "Profile names and scores are stored in your browser local storage. Politiscales Analyser does not send them to an application server."}</p>
        <h2>Google AdSense</h2>
        <p>{language === "fr" ? "Si vous acceptez les publicités, Google AdSense peut traiter des identifiants, cookies, données techniques et interactions conformément à ses propres politiques. Vous pouvez retirer ce choix depuis le pied de page." : "If you accept advertising, Google AdSense may process identifiers, cookies, technical data, and interactions under its own policies. You can revisit this choice from the footer."}</p>
        <h2>{language === "fr" ? "Vos contrôles" : "Your controls"}</h2>
        <p>{language === "fr" ? "Vous pouvez refuser la publicité, effacer les données du site depuis votre navigateur et exporter vos profils en JSON." : "You can reject advertising, clear site data in your browser, and export profiles as JSON."}</p>
      </section>
    </>
  );
}

export function LegalView({ language }: { language: Language }) {
  return (
    <>
      <PageHeading title={language === "fr" ? "Mentions légales" : "Legal notice"} description="Politiscales Analyser" />
      <section className="legal-copy">
        <h2>{language === "fr" ? "Éditeur" : "Publisher"}</h2>
        <p>Kenzi Lali · Political Spectrum Analyzer · France.</p>
        <h2>{language === "fr" ? "Hébergement" : "Hosting"}</h2>
        <p>Vercel Inc., 440 N Barranca Ave #4133, Covina, CA 91723, United States.</p>
        <h2>{language === "fr" ? "Responsabilité" : "Liability"}</h2>
        <p>{language === "fr" ? "Les résultats sont des estimations heuristiques et ne constituent ni un diagnostic, ni un conseil électoral, juridique ou scientifique." : "Results are heuristic estimates and are not diagnostic, electoral, legal, or scientific advice."}</p>
      </section>
    </>
  );
}
