import { describe, expect, it } from "vitest";
import { analyzeProfile } from "./analysis";
import { DEFAULT_SCORES } from "./constants";
import { SCORING_MODEL_VERSION } from "./model";

describe("personalized profile analysis", () => {
  it("reports a centered neutral profile as low intensity and coherent", () => {
    const result = analyzeProfile(
      { id: "neutral", name: "Neutral", scores: { ...DEFAULT_SCORES }, modelVersion: SCORING_MODEL_VERSION },
      "fr",
    );

    expect(result.intensityScore).toBe(0);
    expect(result.coherenceScore).toBe(50);
    expect(result.interpretabilityScore).toBeLessThan(10);
    expect(result.archetype).toBe("Profil équilibré ou composite");
    expect(result.dominant).toHaveLength(0);
    expect(result.weakest).toHaveLength(0);
    expect(result.scoreNotes).toHaveLength(16);
    expect(result.balances).toHaveLength(8);
  });

  it("detects cross-axis tensions", () => {
    const result = analyzeProfile(
      {
        id: "mixed",
        name: "Mixed",
        modelVersion: SCORING_MODEL_VERSION,
        scores: {
          ...DEFAULT_SCORES,
          capitalisme: 75,
          regulation: 72,
          progressisme: 80,
          justice_punitive: 70,
        },
      },
      "fr",
    );

    expect(result.tensions.some((text) => text.includes("régulation"))).toBe(true);
    expect(result.tensions.some((text) => text.includes("punitive"))).toBe(true);
    expect(result.diagnosticNotes).toHaveLength(2);
  });
});
