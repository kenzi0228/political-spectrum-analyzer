import { AXIS_PAIRS, axisLabel } from "./constants";
import { computeProjection, quadrant } from "./scoring";
import type { AxisKey, Language, Profile } from "./types";

export interface AnalysisResult {
  summary: string;
  highlights: string[];
  dominant: AxisKey[];
  weakest: AxisKey[];
  balances: Array<{
    left: AxisKey;
    right: AxisKey;
    delta: number;
    intensity: number;
  }>;
  tensions: string[];
  scoreNotes: Array<{ axis: AxisKey; score: number; note: string }>;
}

export const analyzeProfile = (
  profile: Profile,
  language: Language,
): AnalysisResult => {
  const projection = computeProjection(profile.scores);
  const ranked = Object.entries(profile.scores).sort((a, b) => b[1] - a[1]) as [
    AxisKey,
    number,
  ][];
  const dominant = ranked.slice(0, 4).map(([axis]) => axis);
  const weakest = ranked.slice(-4).reverse().map(([axis]) => axis);
  const balances = AXIS_PAIRS.map(({ left, right }) => ({
    left,
    right,
    delta: profile.scores[left] - profile.scores[right],
    intensity: (profile.scores[left] + profile.scores[right]) / 2,
  }));
  const tensions = balances
    .filter(({ intensity, delta }) => intensity >= 62 && Math.abs(delta) <= 18)
    .map(({ left, right }) =>
      language === "fr"
        ? `${axisLabel(left, language)} et ${axisLabel(right, language)} sont simultanement eleves: cette opposition structure le profil sans se resoudre nettement.`
        : `${axisLabel(left, language)} and ${axisLabel(right, language)} are both high: this opposition structures the profile without resolving clearly.`,
    );

  const crossTensions: string[] = [];
  const s = profile.scores;
  if (s.capitalisme >= 60 && s.regulation >= 60) {
    crossTensions.push(
      language === "fr"
        ? "Le soutien au marche coexiste avec une attente forte de regulation."
        : "Support for markets coexists with a strong expectation of regulation.",
    );
  }
  if (s.progressisme >= 60 && s.justice_punitive >= 60) {
    crossTensions.push(
      language === "fr"
        ? "Le progressisme social coexiste avec une conception punitive de la justice."
        : "Social progressivism coexists with a punitive conception of justice.",
    );
  }
  if (s.internationalisme >= 60 && s.nationalisme >= 60) {
    crossTensions.push(
      language === "fr"
        ? "L'ouverture internationale et l'attachement national sont tous deux affirmes."
        : "International openness and national attachment are both strongly expressed.",
    );
  }

  const q = quadrant(projection.x, projection.y, language);
  const distance = Math.hypot(projection.x, projection.y);
  const summary =
    language === "fr"
      ? `${profile.name} se situe dans la zone ${q.toLowerCase()} (${projection.x.toFixed(2)}, ${projection.y.toFixed(2)}). ${distance < 1 ? "La position reste proche du centre, ce qui rend les axes detailles plus informatifs que l'etiquette de quadrant." : "La distance au centre indique une orientation lisible, sans resumer a elle seule les 16 scores."}`
      : `${profile.name} is located in the ${q.toLowerCase()} area (${projection.x.toFixed(2)}, ${projection.y.toFixed(2)}). ${distance < 1 ? "The position remains close to the center, making the detailed axes more informative than the quadrant label." : "The distance from the center indicates a readable orientation without summarizing all 16 scores."}`;

  const highlights = [
    language === "fr"
      ? `Axes les plus affirmes: ${dominant.map((axis) => axisLabel(axis, language)).join(", ")}.`
      : `Most pronounced axes: ${dominant.map((axis) => axisLabel(axis, language)).join(", ")}.`,
    language === "fr"
      ? `Orientation economique brute: ${projection.xRaw > 0 ? "droite" : "gauche"} (${projection.xRaw.toFixed(1)}).`
      : `Raw economic orientation: ${projection.xRaw > 0 ? "right" : "left"} (${projection.xRaw.toFixed(1)}).`,
    language === "fr"
      ? `Orientation sociale brute: ${projection.yRaw > 0 ? "autoritaire" : "libertaire"} (${projection.yRaw.toFixed(1)}).`
      : `Raw social orientation: ${projection.yRaw > 0 ? "authoritarian" : "libertarian"} (${projection.yRaw.toFixed(1)}).`,
  ];

  const scoreNotes = ranked.map(([axis, score]) => {
    const level =
      score >= 75
        ? language === "fr"
          ? "position tres affirmee"
          : "very strong position"
        : score >= 60
          ? language === "fr"
            ? "orientation nette"
            : "clear orientation"
          : score >= 40
            ? language === "fr"
              ? "position moderee"
              : "moderate position"
            : language === "fr"
              ? "faible adhesion"
              : "low endorsement";
    return { axis, score, note: level };
  });

  return {
    summary,
    highlights,
    dominant,
    weakest,
    balances,
    tensions: [...tensions, ...crossTensions],
    scoreNotes,
  };
};
