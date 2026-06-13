import { describe, expect, it } from "vitest";
import { DEFAULT_SCORES } from "./constants";
import { SCORING_MODEL_VERSION } from "./model";
import type { Profile, ReferenceProfile } from "./types";
import {
  EMPTY_FILTERS,
  filterReferenceProfiles,
  findNearestReferences,
} from "./views/VisualizationView";

const reference = (
  name: string,
  x: number,
  y: number,
  country = "France",
): ReferenceProfile => ({
  name,
  period: "21st century",
  x,
  y,
  country,
  display_group: "Thinker",
  ideology_family: "General",
  confidence: "high",
  century: "21st century",
  role_category: "Thinker",
  gender: "female",
  notes: "",
  source: "",
  is_estimated: true,
  provenanceStatus: "unsourced",
});

describe("visualization reference context", () => {
  it("keeps every reference when no filter is selected", () => {
    const references = [
      reference("A", 0, 0, "France"),
      reference("B", 1, 1, "Germany"),
    ];

    expect(filterReferenceProfiles(references, EMPTY_FILTERS)).toEqual(references);
    expect(
      filterReferenceProfiles(references, {
        ...EMPTY_FILTERS,
        country: ["France"],
      }).map((item) => item.name),
    ).toEqual(["A"]);
  });

  it("returns the three closest references to the active profile", () => {
    const profile: Profile = {
      id: "profile",
      name: "Profile",
      scores: { ...DEFAULT_SCORES },
      modelVersion: SCORING_MODEL_VERSION,
    };
    const references = [
      reference("Far", 3, 3),
      reference("Closest", -0.17, -0.08),
      reference("Third", 0.3, 0.2),
      reference("Second", 0, 0),
    ];

    expect(
      findNearestReferences(references, profile).map(({ reference }) => reference.name),
    ).toEqual(["Closest", "Second", "Third"]);
  });
});
