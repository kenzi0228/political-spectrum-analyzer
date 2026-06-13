import type { AxisKey, Scores } from "./types";

export const AXIS_PAIRS: ReadonlyArray<{
  left: AxisKey;
  right: AxisKey;
  group: "society" | "economy" | "strategy";
}> = [
  { left: "constructivisme", right: "essentialisme", group: "society" },
  { left: "justice_rehabilitative", right: "justice_punitive", group: "society" },
  { left: "progressisme", right: "conservatisme", group: "society" },
  { left: "internationalisme", right: "nationalisme", group: "society" },
  { left: "communisme", right: "capitalisme", group: "economy" },
  { left: "regulation", right: "laissez_faire", group: "economy" },
  { left: "ecologie", right: "productivisme", group: "economy" },
  { left: "revolution", right: "reformisme", group: "strategy" },
];

export const AXES = AXIS_PAIRS.flatMap(({ left, right }) => [left, right]);

export const DEFAULT_SCORES = Object.fromEntries(
  AXES.map((axis) => [axis, 50]),
) as Scores;

export const PROFILE_COLORS = [
  "#00a6a6",
  "#f05d5e",
  "#f2b134",
  "#6f7bf7",
  "#bc6ff1",
];

export const axisLabel = (axis: AxisKey, language: "fr" | "en"): string => {
  const labels: Record<AxisKey, [string, string]> = {
    constructivisme: ["Constructivisme", "Constructivism"],
    essentialisme: ["Essentialisme", "Essentialism"],
    justice_rehabilitative: ["Justice réhabilitative", "Rehabilitative justice"],
    justice_punitive: ["Justice punitive", "Punitive justice"],
    progressisme: ["Progressisme", "Progressivism"],
    conservatisme: ["Conservatisme", "Conservatism"],
    internationalisme: ["Internationalisme", "Internationalism"],
    nationalisme: ["Nationalisme", "Nationalism"],
    communisme: ["Communisme", "Communism"],
    capitalisme: ["Capitalisme", "Capitalism"],
    regulation: ["Régulation", "Regulation"],
    laissez_faire: ["Laissez-faire", "Laissez-faire"],
    ecologie: ["Écologie", "Ecology"],
    productivisme: ["Productivisme", "Productivism"],
    revolution: ["Révolution", "Revolution"],
    reformisme: ["Réformisme", "Reformism"],
  };
  return labels[axis][language === "fr" ? 0 : 1];
};
