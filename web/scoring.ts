import type { AxisKey, Projection, Scores } from "./types";
import {
  MAP_SCALE,
  MODEL_ADJUSTMENTS,
  MODEL_BLOCKS,
  NORMALIZATION_SCALE,
} from "./model";

export interface AxisContribution {
  axis: AxisKey;
  xWeight: number;
  yWeight: number;
  xContribution: number;
  yContribution: number;
}

const weightedBlock = (
  scores: Scores,
  terms: readonly { axis: AxisKey; weight: number }[],
): number =>
  terms.reduce((sum, { axis, weight }) => sum + scores[axis] * weight, 0);

const axisWeights = (target: "x" | "y"): Partial<Record<AxisKey, number>> => {
  const weights: Partial<Record<AxisKey, number>> = {};
  const add = (axis: AxisKey, weight: number) => {
    weights[axis] = (weights[axis] ?? 0) + weight;
  };
  if (target === "x") {
    MODEL_BLOCKS.economicLeft.forEach(({ axis, weight }) => add(axis, -weight));
    MODEL_BLOCKS.economicRight.forEach(({ axis, weight }) => add(axis, weight));
  } else {
    MODEL_BLOCKS.socialLibertarian.forEach(({ axis, weight }) => add(axis, -weight));
    MODEL_BLOCKS.socialAuthoritarian.forEach(({ axis, weight }) => add(axis, weight));
  }
  MODEL_ADJUSTMENTS.filter((adjustment) => adjustment.target === target).forEach(
    ({ positive, negative, weight }) => {
      add(positive, weight);
      add(negative, -weight);
    },
  );
  return weights;
};

const X_WEIGHTS = axisWeights("x");
const Y_WEIGHTS = axisWeights("y");

export const sigmoidScaled = (value: number): number =>
  2 / (1 + Math.exp(-2 * value)) - 1;

export const computeProjection = (scores: Scores): Projection => {
  const economicLeft = weightedBlock(scores, MODEL_BLOCKS.economicLeft);
  const economicRight = weightedBlock(scores, MODEL_BLOCKS.economicRight);
  const socialLibertarian = weightedBlock(scores, MODEL_BLOCKS.socialLibertarian);
  const socialAuthoritarian = weightedBlock(scores, MODEL_BLOCKS.socialAuthoritarian);
  const [economicRule, socialRule, strategicRule] = MODEL_ADJUSTMENTS;
  const economicAdjustment =
    economicRule.weight *
    (scores[economicRule.positive] - scores[economicRule.negative]);
  const socialAdjustment =
    socialRule.weight * (scores[socialRule.positive] - scores[socialRule.negative]);
  const strategicAdjustment =
    strategicRule.weight *
    (scores[strategicRule.positive] - scores[strategicRule.negative]);
  const xRaw = economicRight - economicLeft + economicAdjustment;
  const yRaw =
    socialAuthoritarian -
    socialLibertarian +
    socialAdjustment +
    strategicAdjustment;

  return {
    x: Number((MAP_SCALE * sigmoidScaled(xRaw / NORMALIZATION_SCALE)).toFixed(3)),
    y: Number((MAP_SCALE * sigmoidScaled(yRaw / NORMALIZATION_SCALE)).toFixed(3)),
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

export const computeAxisContributions = (scores: Scores): AxisContribution[] =>
  (Object.keys(scores) as AxisKey[]).map((axis) => {
    const xWeight = X_WEIGHTS[axis] ?? 0;
    const yWeight = Y_WEIGHTS[axis] ?? 0;
    return {
      axis,
      xWeight,
      yWeight,
      xContribution: scores[axis] * xWeight,
      yContribution: scores[axis] * yWeight,
    };
  });

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
