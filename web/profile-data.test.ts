import { describe, expect, it } from "vitest";
import { DEFAULT_SCORES } from "./constants";
import { SCORING_MODEL_VERSION } from "./model";
import {
  createDefaultProfile,
  parseImportedProfile,
  parseStoredProfiles,
  serializeProfiles,
} from "./profile-data";

describe("profile data validation", () => {
  it("migrates the legacy profile array and serializes a versioned envelope", () => {
    const legacy = [
      { id: "legacy", name: "Legacy", scores: { ...DEFAULT_SCORES } },
    ];
    const profiles = parseStoredProfiles(JSON.stringify(legacy));

    expect(profiles).toEqual([
      { ...legacy[0], modelVersion: SCORING_MODEL_VERSION },
    ]);
    expect(JSON.parse(serializeProfiles(profiles!))).toMatchObject({
      version: 3,
      profiles: legacy,
    });
  });

  it("rejects semantically invalid local data", () => {
    expect(parseStoredProfiles("[]")).toBeNull();
    expect(
      parseStoredProfiles(
        JSON.stringify([
          {
            id: "broken",
            name: "Broken",
            scores: { ...DEFAULT_SCORES, communisme: 140 },
          },
        ]),
      ),
    ).toBeNull();
  });

  it("rejects malformed, partial and out-of-range imports", () => {
    const current = createDefaultProfile();

    expect(() => parseImportedProfile("{", current)).toThrow(/JSON valide/);
    expect(() =>
      parseImportedProfile(JSON.stringify({ scores: { communisme: 50 } }), current),
    ).toThrow(/constructivisme/);
    expect(() =>
      parseImportedProfile(
        JSON.stringify({
          schema: "political_spectrum_profile.v1",
          scores: { ...DEFAULT_SCORES, nationalisme: -1 },
        }),
        current,
      ),
    ).toThrow(/0 et 100/);
  });
});
