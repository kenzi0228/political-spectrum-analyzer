import type { AxisKey } from "./types";

export const SCORING_MODEL_VERSION = "scoring-model-v2.1";
export const NORMALIZATION_SCALE = 120;
export const MAP_SCALE = 4;

export type WeightedBlockName =
  | "economicLeft"
  | "economicRight"
  | "socialLibertarian"
  | "socialAuthoritarian";

export interface ModelTerm {
  axis: AxisKey;
  weight: number;
}

export interface ModelAdjustment {
  target: "x" | "y";
  positive: AxisKey;
  negative: AxisKey;
  weight: number;
  label: string;
}

export const MODEL_BLOCKS: Record<WeightedBlockName, readonly ModelTerm[]> = {
  economicLeft: [
    { axis: "communisme", weight: 0.9 },
    { axis: "regulation", weight: 0.7 },
    { axis: "ecologie", weight: 0.35 },
    { axis: "revolution", weight: 0.25 },
  ],
  economicRight: [
    { axis: "capitalisme", weight: 0.9 },
    { axis: "laissez_faire", weight: 0.75 },
    { axis: "productivisme", weight: 0.25 },
    { axis: "reformisme", weight: 0.2 },
  ],
  socialLibertarian: [
    { axis: "constructivisme", weight: 0.7 },
    { axis: "justice_rehabilitative", weight: 0.65 },
    { axis: "progressisme", weight: 0.7 },
    { axis: "internationalisme", weight: 0.5 },
  ],
  socialAuthoritarian: [
    { axis: "essentialisme", weight: 0.6 },
    { axis: "justice_punitive", weight: 0.7 },
    { axis: "conservatisme", weight: 0.7 },
    { axis: "nationalisme", weight: 0.5 },
  ],
};

export const MODEL_ADJUSTMENTS: readonly ModelAdjustment[] = [
  {
    target: "x",
    positive: "productivisme",
    negative: "ecologie",
    weight: 0.12,
    label: "productive-ecological adjustment",
  },
  {
    target: "y",
    positive: "nationalisme",
    negative: "internationalisme",
    weight: 0.1,
    label: "national-international adjustment",
  },
  {
    target: "y",
    positive: "revolution",
    negative: "reformisme",
    weight: 0.08,
    label: "strategic adjustment",
  },
];

export const MODEL_STATUS = {
  validation: "editorial-heuristic",
  calibrated: false,
  coordinateRange: [-4, 4] as const,
} as const;
