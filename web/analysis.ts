import { AXIS_PAIRS, axisLabel } from "./constants";
import { computeProjection, quadrant } from "./scoring";
import type { AxisKey, Language, Profile, Scores } from "./types";

interface Balance {
  left: AxisKey;
  right: AxisKey;
  delta: number;
  intensity: number;
  dimension: string;
  leadingSide: string;
  reading: string;
}

export interface AnalysisResult {
  archetype: string;
  summary: string;
  intensityScore: number;
  coherenceScore: number;
  interpretabilityScore: number;
  interpretabilityLabel: string;
  centerOfGravity: string;
  economicReading: string;
  societalReading: string;
  strategicReading: string;
  diagnosticNotes: string[];
  highlights: string[];
  dominant: AxisKey[];
  weakest: AxisKey[];
  balances: Balance[];
  tensions: string[];
  scoreNotes: Array<{ axis: AxisKey; score: number; level: string; note: string }>;
}

const pairDimensions: Record<AxisKey, [string, string]> = {
  constructivisme: ["Philosophie sociale", "Social philosophy"],
  essentialisme: ["Philosophie sociale", "Social philosophy"],
  justice_rehabilitative: ["Orientation de la justice", "Justice orientation"],
  justice_punitive: ["Orientation de la justice", "Justice orientation"],
  progressisme: ["Changement social", "Social change"],
  conservatisme: ["Changement social", "Social change"],
  internationalisme: ["Communauté politique", "Political community"],
  nationalisme: ["Communauté politique", "Political community"],
  communisme: ["Modèle de propriété", "Ownership model"],
  capitalisme: ["Modèle de propriété", "Ownership model"],
  regulation: ["Gouvernance du marché", "Market governance"],
  laissez_faire: ["Gouvernance du marché", "Market governance"],
  ecologie: ["Écologie et production", "Ecology and production"],
  productivisme: ["Écologie et production", "Ecology and production"],
  revolution: ["Stratégie politique", "Political strategy"],
  reformisme: ["Stratégie politique", "Political strategy"],
};

const average = (scores: Scores, axes: AxisKey[]) =>
  axes.reduce((total, axis) => total + scores[axis], 0) / axes.length;

const scoreLevel = (score: number, language: Language) => {
  if (score >= 75) return language === "fr" ? "Très élevé" : "Very high";
  if (score >= 60) return language === "fr" ? "Élevé" : "High";
  if (score >= 40) return language === "fr" ? "Modéré" : "Moderate";
  if (score >= 25) return language === "fr" ? "Faible" : "Low";
  return language === "fr" ? "Très faible" : "Very low";
};

const scoreMeaning = (axis: AxisKey, score: number, language: Language) => {
  const strength =
    score >= 75
      ? language === "fr" ? "Marqueur très fort." : "Very strong marker."
      : score >= 60
        ? language === "fr" ? "Marqueur net." : "Clear marker."
        : score >= 40
          ? language === "fr" ? "Signal modéré." : "Moderate signal."
          : score >= 25
            ? language === "fr" ? "Signal faible." : "Weak signal."
            : language === "fr" ? "Signal très faible ou marginal." : "Very weak or marginal signal.";
  const meanings: Record<AxisKey, [string, string]> = {
    constructivisme: ["Lecture des normes et identités comme des constructions historiques et sociales.", "Reads norms and identities as historical and social constructions."],
    essentialisme: ["Valorise des catégories stables et une lecture plus fixe de la société.", "Values stable categories and a more fixed reading of society."],
    justice_rehabilitative: ["Privilégie prévention, réinsertion et réhabilitation.", "Prioritizes prevention, reintegration, and rehabilitation."],
    justice_punitive: ["Met l’accent sur l’ordre, la sanction et la dissuasion.", "Emphasizes order, punishment, and deterrence."],
    progressisme: ["Soutient l’évolution des normes et l’élargissement des droits.", "Supports evolving norms and expanding rights."],
    conservatisme: ["Valorise continuité, tradition et stabilité institutionnelle.", "Values continuity, tradition, and institutional stability."],
    internationalisme: ["Favorise coopération internationale et solidarité transfrontalière.", "Favors international cooperation and cross-border solidarity."],
    nationalisme: ["Privilégie souveraineté, cohésion et intérêt collectif national.", "Prioritizes sovereignty, cohesion, and national collective interest."],
    communisme: ["Traduit redistribution forte, propriété collective ou critique du capitalisme.", "Signals strong redistribution, collective ownership, or criticism of capitalism."],
    capitalisme: ["Accorde de l’importance aux marchés, à la propriété privée et à l’entrepreneuriat.", "Values markets, private ownership, and entrepreneurship."],
    regulation: ["Soutient l’encadrement public et la correction institutionnelle des marchés.", "Supports public oversight and institutional market correction."],
    laissez_faire: ["Favorise autonomie du marché, dérégulation et intervention limitée.", "Favors market autonomy, deregulation, and limited intervention."],
    ecologie: ["Accorde du poids aux limites environnementales et à la durabilité.", "Gives weight to environmental limits and sustainability."],
    productivisme: ["Valorise production, croissance, infrastructures et capacité industrielle.", "Values production, growth, infrastructure, and industrial capacity."],
    revolution: ["Se montre ouvert à la rupture et à la transformation systémique.", "Is open to rupture and systemic transformation."],
    reformisme: ["Préfère le changement progressif dans la continuité institutionnelle.", "Prefers gradual change within institutional continuity."],
  };
  return `${strength} ${meanings[axis][language === "fr" ? 0 : 1]}`;
};

const computeIntensity = (scores: Scores) =>
  Number(
    (
      (Object.values(scores).reduce((sum, score) => sum + Math.abs(score - 50), 0) /
        Object.values(scores).length) *
      2
    ).toFixed(1),
  );

const computeCoherence = (scores: Scores) => {
  const pairScores = AXIS_PAIRS.map(({ left, right }) => {
    const leftScore = scores[left];
    const rightScore = scores[right];
    const clarity = Math.min(1, Math.abs(leftScore - rightScore) / 50);
    const activation = Math.min(
      1,
      (Math.abs(leftScore - 50) + Math.abs(rightScore - 50)) / 100,
    );
    const simultaneousHigh = Math.max(0, (Math.min(leftScore, rightScore) - 50) / 50);
    return Math.max(
      0,
      Math.min(
        100,
        50 + 50 * clarity * (0.5 + 0.5 * activation) - 60 * simultaneousHigh,
      ),
    );
  });

  let crossPenalty = 0;
  const crossPairs: Array<[AxisKey, AxisKey]> = [
    ["capitalisme", "regulation"],
    ["progressisme", "justice_punitive"],
    ["ecologie", "productivisme"],
    ["internationalisme", "nationalisme"],
  ];
  for (const [left, right] of crossPairs) {
    crossPenalty += Math.max(0, Math.min(scores[left], scores[right]) - 55) * 0.6;
  }
  const base = pairScores.reduce((sum, score) => sum + score, 0) / pairScores.length;
  return Number(Math.max(0, Math.min(100, base - crossPenalty)).toFixed(1));
};

export const analyzeProfile = (
  profile: Profile,
  language: Language,
): AnalysisResult => {
  const projection = computeProjection(profile.scores);
  const scores = profile.scores;
  const ranked = Object.entries(scores).sort((a, b) => b[1] - a[1]) as [
    AxisKey,
    number,
  ][];
  const dominant = ranked.filter(([, score]) => score >= 60).slice(0, 5).map(([axis]) => axis);
  const weakest = ranked.filter(([, score]) => score <= 35).slice(-5).reverse().map(([axis]) => axis);
  const intensityScore = computeIntensity(scores);
  const coherenceScore = computeCoherence(scores);
  const distance = Math.hypot(projection.x, projection.y);
  const interpretabilityScore = Number(
    Math.min(100, intensityScore * 0.7 + (distance / Math.sqrt(32)) * 30).toFixed(1),
  );
  const interpretabilityLabel =
    interpretabilityScore >= 65
      ? language === "fr" ? "Confiance interprétative élevée" : "High interpretive confidence"
      : interpretabilityScore >= 35
        ? language === "fr" ? "Confiance interprétative modérée" : "Moderate interpretive confidence"
        : language === "fr" ? "Confiance interprétative faible" : "Low interpretive confidence";

  const leftAverage = average(scores, ["communisme", "regulation", "ecologie"]);
  const rightAverage = average(scores, ["capitalisme", "laissez_faire", "productivisme"]);
  const progressiveAverage = average(scores, [
    "constructivisme",
    "justice_rehabilitative",
    "progressisme",
    "internationalisme",
  ]);
  const conservativeAverage = average(scores, [
    "essentialisme",
    "justice_punitive",
    "conservatisme",
    "nationalisme",
  ]);

  const economicSide =
    leftAverage > rightAverage + 8 ? "left" : rightAverage > leftAverage + 8 ? "right" : "center";
  const socialSide =
    progressiveAverage > conservativeAverage + 8
      ? "progressive"
      : conservativeAverage > progressiveAverage + 8
        ? "conservative"
        : "mixed";
  const strategySide =
    scores.revolution > scores.reformisme + 10
      ? "rupture"
      : scores.reformisme > scores.revolution + 10
        ? "reform"
        : "balanced";

  const archetypes = {
    fr: {
      "left-progressive": "Profil de gauche progressiste",
      "left-conservative": "Profil de gauche socialement conservateur",
      "right-progressive": "Profil libéral-progressiste",
      "right-conservative": "Profil conservateur orienté vers le marché",
      "center-progressive": "Profil centriste social-progressiste",
      "center-conservative": "Profil centriste orienté vers l’ordre",
      "center-mixed": "Profil équilibré ou composite",
    },
    en: {
      "left-progressive": "Progressive left profile",
      "left-conservative": "Socially conservative left profile",
      "right-progressive": "Liberal-market progressive profile",
      "right-conservative": "Conservative market-oriented profile",
      "center-progressive": "Social-progressive centrist profile",
      "center-conservative": "Order-oriented centrist profile",
      "center-mixed": "Balanced or composite profile",
    },
  };
  const archetypeKey = `${economicSide}-${socialSide}` as keyof typeof archetypes.fr;
  const archetype = archetypes[language][archetypeKey] ?? archetypes[language]["center-mixed"];

  const economicReading =
    Math.abs(leftAverage - rightAverage) <= 8
      ? language === "fr"
        ? "Économiquement, le profil combine des signaux interventionnistes et pro-marché plutôt que de suivre une direction unique."
        : "Economically, the profile combines interventionist and market-oriented signals rather than following a single direction."
      : leftAverage > rightAverage
        ? scores.ecologie >= 65
          ? language === "fr"
            ? "Économiquement, le profil penche vers l’intervention publique, avec une composante écologique et réglementaire marquée."
            : "Economically, the profile leans interventionist, with a strong ecological and regulatory component."
          : language === "fr"
            ? "Économiquement, le profil penche vers la redistribution, l’intervention publique et la correction collective du marché."
            : "Economically, the profile leans toward redistribution, public intervention, and collective market correction."
        : scores.productivisme >= 65
          ? language === "fr"
            ? "Économiquement, le profil penche vers le marché, avec un accent prononcé sur la production, la croissance et les capacités."
            : "Economically, the profile leans market-oriented, with a strong emphasis on production, growth, and capacity."
          : language === "fr"
            ? "Économiquement, le profil penche vers l’autonomie du marché, l’initiative privée et une intervention plus limitée."
            : "Economically, the profile leans toward market autonomy, private initiative, and lower intervention.";

  const societalReading =
    Math.abs(progressiveAverage - conservativeAverage) <= 8
      ? language === "fr"
        ? "Sur le plan sociétal, le profil combine ouverture au changement et recherche d’ordre, produisant une posture composite."
        : "Societally, the profile combines openness to change with order-oriented signals, producing a mixed posture."
      : progressiveAverage > conservativeAverage
        ? scores.internationalisme >= 65
          ? language === "fr"
            ? "Sur le plan sociétal, le profil penche vers le progressisme, avec une forte orientation internationale et coopérative."
            : "Societally, the profile leans progressive, with strong international and cooperative orientation."
          : language === "fr"
            ? "Sur le plan sociétal, le profil penche vers le progressisme, la réforme des normes et l’ouverture au changement."
            : "Societally, the profile leans progressive, reform-oriented, and open to social change."
        : scores.nationalisme >= 65
          ? language === "fr"
            ? "Sur le plan sociétal, le profil privilégie l’ordre et la continuité, avec une composante de souveraineté nationale prononcée."
            : "Societally, the profile leans order-oriented, with a pronounced national-sovereignty component."
          : language === "fr"
            ? "Sur le plan sociétal, le profil privilégie davantage la stabilité, la continuité et l’ordre."
            : "Societally, the profile leans toward stability, continuity, and order.";

  const strategicReading =
    strategySide === "balanced"
      ? language === "fr"
        ? "Stratégiquement, le profil équilibre l’instinct de transformation systémique et la réforme institutionnelle progressive."
        : "Strategically, the profile balances systemic transformation with gradual institutional reform."
      : strategySide === "rupture"
        ? language === "fr"
          ? "Stratégiquement, le profil est davantage orienté vers la rupture et la transformation profonde du système."
          : "Strategically, the profile is more rupture-oriented and receptive to deep systemic transformation."
        : language === "fr"
          ? "Stratégiquement, le profil est davantage réformiste et privilégie le changement progressif par les institutions."
          : "Strategically, the profile is more reformist and favors gradual institutional change.";

  const economicGravity =
    economicSide === "left"
      ? language === "fr" ? "gauche économique" : "economic left"
      : economicSide === "right"
        ? language === "fr" ? "droite économique" : "economic right"
        : language === "fr" ? "économie composite" : "economically mixed";
  const socialGravity =
    socialSide === "progressive"
      ? language === "fr" ? "progressiste/libertaire" : "progressive/libertarian"
      : socialSide === "conservative"
        ? language === "fr" ? "ordre/conservatisme" : "order-oriented/conservative"
        : language === "fr" ? "société composite" : "socially mixed";
  const strategyGravity =
    strategySide === "rupture"
      ? language === "fr" ? "orienté vers la rupture" : "rupture-oriented"
      : strategySide === "reform"
        ? language === "fr" ? "réformiste" : "reformist"
        : language === "fr" ? "stratégie équilibrée" : "strategically balanced";
  const centerOfGravity = `${economicGravity}, ${socialGravity}, ${strategyGravity}`;

  const balances: Balance[] = AXIS_PAIRS.map(({ left, right }) => {
    const delta = scores[left] - scores[right];
    const intensity = (scores[left] + scores[right]) / 2;
    const dimension = pairDimensions[left][language === "fr" ? 0 : 1];
    const bothHigh = scores[left] >= 60 && scores[right] >= 60;
    const bothLow = scores[left] <= 35 && scores[right] <= 35;
    const leadingSide =
      bothHigh
        ? language === "fr" ? "Tension interne" : "Internally mixed"
        : bothLow
          ? language === "fr" ? "Dimension atténuée" : "Muted"
          : Math.abs(delta) <= 10
            ? language === "fr" ? "Équilibré" : "Balanced"
            : axisLabel(delta > 0 ? left : right, language);
    const reading =
      bothHigh
        ? language === "fr"
          ? `${dimension} : les deux pôles sont élevés ; cette opposition doit être lue comme une tension réelle.`
          : `${dimension}: both poles are high and should be read as a genuine internal tension.`
        : bothLow
          ? language === "fr"
            ? `${dimension} : les deux pôles sont faibles ; cette dimension structure peu le profil.`
            : `${dimension}: both poles are weak, so this dimension does not strongly structure the profile.`
          : Math.abs(delta) <= 10
            ? language === "fr"
              ? `${dimension} : équilibre relatif entre les deux pôles.`
              : `${dimension}: relative balance between both poles.`
            : language === "fr"
              ? `${dimension} : ${axisLabel(delta > 0 ? left : right, language)} domine de ${Math.abs(delta)} points.`
              : `${dimension}: ${axisLabel(delta > 0 ? left : right, language)} leads by ${Math.abs(delta)} points.`;
    return { left, right, delta, intensity, dimension, leadingSide, reading };
  });

  const tensions = balances
    .filter(({ intensity, delta }) => intensity >= 60 && Math.abs(delta) <= 18)
    .map(({ reading }) => reading);
  const crossTensions: string[] = [];
  if (scores.capitalisme >= 60 && scores.regulation >= 60) {
    crossTensions.push(language === "fr" ? "Le soutien au marché coexiste avec une forte attente de régulation publique." : "Market support coexists with a strong expectation of public regulation.");
  }
  if (scores.progressisme >= 60 && scores.justice_punitive >= 60) {
    crossTensions.push(language === "fr" ? "Le progressisme social coexiste avec une conception punitive de la justice." : "Social progressivism coexists with a punitive conception of justice.");
  }
  if (scores.ecologie >= 60 && scores.productivisme >= 60) {
    crossTensions.push(language === "fr" ? "Le profil valorise à la fois les limites écologiques et l’expansion productive." : "The profile values both ecological limits and productive expansion.");
  }
  if (scores.internationalisme >= 60 && scores.nationalisme >= 60) {
    crossTensions.push(language === "fr" ? "L’ouverture internationale coexiste avec des priorités fortes de souveraineté nationale." : "International openness coexists with strong national-sovereignty priorities.");
  }
  const allTensions = [...new Set([...tensions, ...crossTensions])];

  const diagnosticNotes = [
    intensityScore >= 55
      ? language === "fr"
        ? `Intensité élevée (${intensityScore}/100) : plusieurs scores s’éloignent fortement du point neutre.`
        : `High intensity (${intensityScore}/100): several scores are far from the neutral midpoint.`
      : intensityScore <= 25
        ? language === "fr"
          ? `Intensité faible (${intensityScore}/100) : la position graphique doit être interprétée avec prudence.`
          : `Low intensity (${intensityScore}/100): the map position should be read cautiously.`
        : language === "fr"
          ? `Intensité modérée (${intensityScore}/100) : le profil possède des signaux lisibles sans être uniformément extrême.`
          : `Moderate intensity (${intensityScore}/100): the profile has readable signals without being uniformly extreme.`,
    coherenceScore >= 80
      ? language === "fr"
        ? `Clarté directionnelle élevée (${coherenceScore}/100) : peu de pôles opposés sont simultanément élevés.`
        : `High directional clarity (${coherenceScore}/100): few opposing poles are simultaneously high.`
      : coherenceScore >= 55
        ? language === "fr"
          ? `Clarté directionnelle intermédiaire (${coherenceScore}/100) : certaines pressions contradictoires méritent une lecture détaillée.`
          : `Mixed directional clarity (${coherenceScore}/100): some cross-pressures deserve detailed interpretation.`
        : language === "fr"
          ? `Clarté directionnelle faible (${coherenceScore}/100) : les tensions internes sont centrales dans la lecture.`
          : `Low directional clarity (${coherenceScore}/100): internal tensions are central to the reading.`,
  ];

  const q = quadrant(projection.x, projection.y, language);
  const summary =
    language === "fr"
      ? `Cette lecture heuristique rapproche ${profile.name} d’un ${archetype.toLowerCase()} et le situe dans la zone ${q.toLowerCase()} (${projection.x.toFixed(2)}, ${projection.y.toFixed(2)}). ${distance < 1 ? "La proximité du centre invite à privilégier les 16 axes plutôt que l’étiquette de quadrant." : `Le centre de gravité estimé est ${centerOfGravity}.`}`
      : `This heuristic reading places ${profile.name} near a ${archetype.toLowerCase()} and in the ${q.toLowerCase()} area (${projection.x.toFixed(2)}, ${projection.y.toFixed(2)}). ${distance < 1 ? "Its proximity to the center makes the 16 axes more informative than the quadrant label." : `Its estimated center of gravity is ${centerOfGravity}.`}`;

  const highlights = [
    dominant.length
      ? language === "fr"
        ? `Moteurs principaux : ${dominant.slice(0, 3).map((axis) => axisLabel(axis, language)).join(", ")}.`
        : `Core drivers: ${dominant.slice(0, 3).map((axis) => axisLabel(axis, language)).join(", ")}.`
      : language === "fr"
        ? "Aucun axe ne dépasse le seuil de 60/100 : le profil ne possède pas de moteur dominant net."
        : "No axis exceeds the 60/100 threshold: the profile has no clearly dominant driver.",
    ...dominant
      .filter((axis) => scores[axis] >= 60)
      .slice(0, 3)
      .map((axis) =>
        language === "fr"
          ? `${axisLabel(axis, language)} contribue nettement à la direction du profil (${scores[axis]}/100).`
          : `${axisLabel(axis, language)} clearly contributes to the profile direction (${scores[axis]}/100).`,
      ),
    weakest.length
      ? language === "fr"
        ? `Dimensions de faible impact : ${weakest.slice(0, 2).map((axis) => axisLabel(axis, language)).join(", ")}.`
        : `Low-impact dimensions: ${weakest.slice(0, 2).map((axis) => axisLabel(axis, language)).join(", ")}.`
      : language === "fr"
        ? "Aucun axe ne se situe sous le seuil faible de 35/100."
        : "No axis falls below the low-impact threshold of 35/100.",
    ...(allTensions.length ? [allTensions[0]] : []),
  ].slice(0, 6);

  const scoreNotes = ranked.map(([axis, score]) => ({
    axis,
    score,
    level: scoreLevel(score, language),
    note: scoreMeaning(axis, score, language),
  }));

  return {
    archetype,
    summary,
    intensityScore,
    coherenceScore,
    interpretabilityScore,
    interpretabilityLabel,
    centerOfGravity,
    economicReading,
    societalReading,
    strategicReading,
    diagnosticNotes,
    highlights,
    dominant,
    weakest,
    balances,
    tensions: allTensions,
    scoreNotes,
  };
};
