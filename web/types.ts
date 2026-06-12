export type AxisKey =
  | "constructivisme"
  | "essentialisme"
  | "justice_rehabilitative"
  | "justice_punitive"
  | "progressisme"
  | "conservatisme"
  | "internationalisme"
  | "nationalisme"
  | "communisme"
  | "capitalisme"
  | "regulation"
  | "laissez_faire"
  | "ecologie"
  | "productivisme"
  | "revolution"
  | "reformisme";

export type Scores = Record<AxisKey, number>;

export interface Profile {
  id: string;
  name: string;
  scores: Scores;
}

export interface Projection {
  x: number;
  y: number;
  xRaw: number;
  yRaw: number;
  economicLeft: number;
  economicRight: number;
  socialLibertarian: number;
  socialAuthoritarian: number;
  economicAdjustment: number;
  socialAdjustment: number;
  strategicAdjustment: number;
}

export interface ReferenceProfile {
  name: string;
  display_group: string;
  country: string;
  ideology_family: string;
  x: number;
  y: number;
  confidence: string;
  century: string;
  role_category: string;
  gender: string;
  notes: string;
}

export type ViewKey =
  | "input"
  | "visualization"
  | "analysis"
  | "comparison"
  | "methodology";

export type Language = "fr" | "en";
