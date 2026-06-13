import { describe, expect, it } from "vitest";
import { computeProjectionDispersion } from "./views/ComparisonView";

describe("projection dispersion", () => {
  it("uses the RMS distance to the centroid", () => {
    expect(
      computeProjectionDispersion([
        { x: 0, y: 0 },
        { x: 2, y: 0 },
      ]),
    ).toBe(1);
    expect(
      computeProjectionDispersion([
        { x: -1, y: 0 },
        { x: 1, y: 0 },
        { x: 0, y: Math.sqrt(3) },
      ]),
    ).toBeCloseTo(1.1547, 4);
  });

  it("returns zero for fewer than two profiles", () => {
    expect(computeProjectionDispersion([])).toBe(0);
    expect(computeProjectionDispersion([{ x: 1, y: 2 }])).toBe(0);
  });
});
