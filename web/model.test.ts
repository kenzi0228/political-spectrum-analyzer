import { describe, expect, it } from "vitest";
import { AXES, DEFAULT_SCORES } from "./constants";
import { computeAxisContributions, computeProjection } from "./scoring";

describe("scoring model invariants", () => {
  it("keeps every projection within the documented map bounds", () => {
    for (const value of [0, 25, 50, 75, 100]) {
      const scores = Object.fromEntries(AXES.map((axis) => [axis, value])) as typeof DEFAULT_SCORES;
      const projection = computeProjection(scores);
      expect(Math.abs(projection.x)).toBeLessThanOrEqual(4);
      expect(Math.abs(projection.y)).toBeLessThanOrEqual(4);
    }
  });

  it("moves monotonically right when capitalism increases in isolation", () => {
    const low = computeProjection({ ...DEFAULT_SCORES, capitalisme: 10 });
    const high = computeProjection({ ...DEFAULT_SCORES, capitalisme: 90 });
    expect(high.x).toBeGreaterThan(low.x);
  });

  it("uses the same declarative weights for explanations and raw projection", () => {
    const scores = { ...DEFAULT_SCORES, capitalisme: 72, regulation: 31 };
    const projection = computeProjection(scores);
    const contributions = computeAxisContributions(scores);
    expect(contributions.reduce((sum, item) => sum + item.xContribution, 0)).toBeCloseTo(projection.xRaw);
    expect(contributions.reduce((sum, item) => sum + item.yContribution, 0)).toBeCloseTo(projection.yRaw);
  });
});
