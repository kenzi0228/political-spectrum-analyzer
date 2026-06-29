import { mkdir, readFile, writeFile } from "node:fs/promises";

const pages = {
  guide: {
    title: "Guide",
    description: "Guide d'utilisation de Politiscales Analyser.",
    body: [
      ["Récupérer ses scores", "Passez le test original sur Politiscales, relevez les pourcentages affichés sur la page de résultats, puis reportez-les dans la saisie de profil. L'outil ne prétend pas être le test original : il sert à interpréter les scores après coup."],
      ["Lire la visualisation", "La carte synthétise deux dimensions : économie sur l'axe horizontal et rapport à l'autorité sur l'axe vertical. Les références sont masquées par défaut afin de ne pas charger visuellement la page ; sélectionnez un filtre ou Any pour les afficher."],
      ["Éviter les surinterprétations", "Une proximité géométrique avec une référence n'est pas une équivalence politique. Elle signale seulement une distance faible selon le modèle éditorial courant et doit être confrontée aux scores détaillés."],
    ],
  },
  methodology: {
    title: "Méthodologie",
    description: "Formule, statut scientifique et limites du modèle de projection.",
    body: [
      ["Statut du modèle", "Le modèle de projection est une heuristique éditoriale versionnée. Il agrège les seize axes en blocs économiques et sociétaux, applique des ajustements secondaires, puis normalise les résultats dans une carte bornée."],
      ["Interprétation des coordonnées", "Les coordonnées x/y servent à explorer une tendance générale. Elles ne remplacent pas les scores bruts, les tensions internes ou le contexte historique d'un profil."],
      ["Validation restante", "La sensibilité du modèle, sa stabilité test-retest et l'accord entre évaluateurs restent à documenter. Le site présente donc les résultats comme des lectures explicables, pas comme des mesures scientifiques définitives."],
    ],
  },
  atlas: {
    title: "Atlas des références",
    description: "Atlas documentaire de 500 personnalités politiques et historiques.",
    body: [
      ["Rôle de l'atlas", "L'atlas fournit des points de comparaison pour situer un profil dans l'espace x/y. Il sert à explorer des proximités, pas à attribuer une étiquette politique définitive."],
      ["Provenance", "Les fiches distinguent les références sourcées et les références encore à vérifier. Cette séparation évite de présenter une estimation éditoriale comme une preuve documentaire."],
      ["Filtres", "Les filtres par pays, famille idéologique, catégorie de rôle, genre, siècle et niveau de confiance permettent de réduire l'ensemble consulté avant de lire les proximités."],
    ],
  },
  privacy: {
    title: "Politique de confidentialité",
    description: "Stockage local des profils et choix publicitaires.",
    body: [
      ["Données de profils", "Les noms de profils et scores saisis sont conservés dans le stockage local du navigateur. Politiscales Analyser n'exploite pas de base de données serveur pour ces profils."],
      ["Publicité", "Google AdSense n'est chargé qu'après un choix publicitaire explicite. Refuser les annonces ne bloque pas les fonctions principales du site."],
      ["Contrôle utilisateur", "L'utilisateur peut exporter ses profils, effacer les données du site depuis son navigateur et rouvrir les choix publicitaires depuis le pied de page."],
    ],
  },
  legal: {
    title: "Mentions légales",
    description: "Informations légales de Politiscales Analyser.",
    body: [
      ["Éditeur", "Politiscales Analyser est édité par Kenzi Lali comme outil indépendant d'analyse et de visualisation de scores politiques."],
      ["Hébergement", "La version web est hébergée sur Vercel. Les pages publiques sont servies comme application web statique."],
      ["Responsabilité", "Les résultats sont des estimations heuristiques. Ils ne constituent pas un conseil électoral, juridique, scientifique ou professionnel."],
    ],
  },
  about: {
    title: "À propos",
    description: "Positionnement éditorial et gouvernance du projet.",
    body: [
      ["Objectif", "Le projet cherche à rendre des scores Politiscales plus lisibles : projection graphique, comparaison, analyse détaillée et documentation des limites."],
      ["Indépendance", "Le site n'est affilié à aucun parti, candidat, institution ou au projet Politiscales original. Le lien vers le test original sert uniquement à orienter les utilisateurs vers la source des scores."],
      ["Gouvernance", "Les corrections de données doivent être justifiées, traçables et documentées. Les estimations non sourcées sont explicitement signalées."],
    ],
  },
};

const renderFallback = ({ title, body }) => `
      <article class="crawlable-content" aria-label="${title}">
        <h1>${title} · Politiscales Analyser</h1>
        ${body.map(([heading, text]) => `<h2>${heading}</h2><p>${text}</p>`).join("\n        ")}
      </article>`;

const source = await readFile("dist/index.html", "utf8");

for (const [route, page] of Object.entries(pages)) {
  const canonical = `https://politiscales-analyser.vercel.app/${route}`;
  const html = source
    .replace("<title>Politiscales Analyser</title>", `<title>${page.title} · Politiscales Analyser</title>`)
    .replace(
      /<meta\s+name="description"\s+content="[^"]*"\s*\/>/,
      `<meta name="description" content="${page.description}" />`,
    )
    .replace(
      /<meta\s+property="og:title"\s+content="[^"]*"\s*\/>/,
      `<meta property="og:title" content="${page.title} · Politiscales Analyser" />`,
    )
    .replace(
      /<meta\s+property="og:url"\s+content="[^"]*"\s*\/>/,
      `<meta property="og:url" content="${canonical}" />`,
    )
    .replace(
      /<link\s+rel="canonical"\s+href="[^"]*"\s*\/>/,
      `<link rel="canonical" href="${canonical}" />`,
    )
    .replace(
      /<div id="root">[\s\S]*?<\/div>\s*<\/body>/,
      `<div id="root">${renderFallback(page)}
    </div>
  </body>`,
    );

  await mkdir(`dist/${route}`, { recursive: true });
  await writeFile(`dist/${route}/index.html`, html, "utf8");
}
