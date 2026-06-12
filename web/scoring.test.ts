import { describe, expect, it } from "vitest";
import { DEFAULT_SCORES } from "./constants";
import { computeProjection, sigmoidScaled } from "./scoring";

describe("scoring model V2", () => {
  it("keeps the sigmoid centered", () => {
    expect(sigmoidScaled(0)).toBe(0);
  });

  it("matches the Python model for the Kenzi example", () => {
    const projection = computeProjection({
      constructivisme: 19,
      essentialisme: 60,
      justice_rehabilitative: 24,
      justice_punitive: 57,
      progressisme: 59,
      conservatisme: 21,
      internationalisme: 33,
      nationalisme: 52,
      communisme: 29,
      capitalisme: 55,
      regulation: 50,
      laissez_faire: 40,
      ecologie: 50,
      productivisme: 40,
      revolution: 40,
      reformisme: 50,
    });
    expect(projection.x).toBeCloseTo(0.323, 3);
    expect(projection.y).toBeCloseTo(1.011, 3);
  });

  it("returns finite coordinates for the neutral profile", () => {
    const projection = computeProjection(DEFAULT_SCORES);
    expect(Number.isFinite(projection.x)).toBe(true);
    expect(Number.isFinite(projection.y)).toBe(true);
  });
});
