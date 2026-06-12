import type { AxisKey, Projection, Scores } from "./types";

const weightedSum = (
  scores: Scores,
  weights: Partial<Record<AxisKey, number>>,
): number =>
  Object.entries(weights).reduce(
    (sum, [axis, weight]) => sum + scores[axis as AxisKey] * (weight ?? 0),
    0,
  );

export const sigmoidScaled = (value: number): number =>
  2 / (1 + Math.exp(-2 * value)) - 1;

export const computeProjection = (scores: Scores): Projection => {
  const economicLeft = weightedSum(scores, {
    communisme: 0.9,
    regulation: 0.7,
    ecologie: 0.35,
    revolution: 0.25,
  });
  const economicRight = weightedSum(scores, {
    capitalisme: 0.9,
    laissez_faire: 0.75,
    productivisme: 0.25,
    reformisme: 0.2,
  });
  const socialLibertarian = weightedSum(scores, {
    constructivisme: 0.7,
    justice_rehabilitative: 0.65,
    progressisme: 0.7,
    internationalisme: 0.5,
  });
  const socialAuthoritarian = weightedSum(scores, {
    essentialisme: 0.6,
    justice_punitive: 0.7,
    conservatisme: 0.7,
    nationalisme: 0.5,
  });

  const economicAdjustment =
    0.12 * (scores.productivisme - scores.ecologie);
  const socialAdjustment =
    0.1 * (scores.nationalisme - scores.internationalisme);
  const strategicAdjustment =
    0.08 * (scores.revolution - scores.reformisme);
  const xRaw = economicRight - economicLeft + economicAdjustment;
  const yRaw =
    socialAuthoritarian -
    socialLibertarian +
    socialAdjustment +
    strategicAdjustment;

  return {
    x: Number((4 * sigmoidScaled(xRaw / 120)).toFixed(3)),
    y: Number((4 * sigmoidScaled(yRaw / 120)).toFixed(3)),
    xRaw,
    yRaw,
    economicLeft,
    economicRight,
    socialLibertarian,
    socialAuthoritarian,
    economicAdjustment,
    socialAdjustment,
    strategicAdjustment,
  };
};

export const quadrant = (
  x: number,
  y: number,
  language: "fr" | "en",
): string => {
  const center = Math.abs(x) < 0.35 && Math.abs(y) < 0.35;
  if (center) return language === "fr" ? "Centre" : "Center";
  if (x < 0 && y < 0)
    return language === "fr" ? "Gauche libertaire" : "Libertarian left";
  if (x < 0 && y >= 0)
    return language === "fr" ? "Gauche autoritaire" : "Authoritarian left";
  if (x >= 0 && y < 0)
    return language === "fr" ? "Droite libertaire" : "Libertarian right";
  return language === "fr" ? "Droite autoritaire" : "Authoritarian right";
};
