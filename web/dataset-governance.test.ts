import { describe, expect, it } from "vitest";
import { loadReferenceProfiles } from "./data";

describe("reference dataset governance", () => {
  it("exposes provenance honestly and disambiguates known period collisions", async () => {
    const references = await loadReferenceProfiles();
    expect(references).toHaveLength(500);
    expect(references.filter((reference) => reference.provenanceStatus === "unsourced")).toHaveLength(500);
    expect(references.map((reference) => reference.name)).toEqual(
      expect.arrayContaining([
        "François Mitterrand (early presidency)",
        "François Mitterrand (later presidency)",
        "Ahmed Ben Bella (presidency)",
        "Ahmed Ben Bella (anti-colonial period)",
      ]),
    );
  });
});
