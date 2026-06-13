import { describe, expect, it } from "vitest";
import { loadReferenceProfiles, parseReferenceProfiles } from "./data";

const HEADER =
  "name,period,display_group,country,ideology_family,x,y,confidence,century,role_category,gender,notes,source,is_estimated";

describe("reference dataset validation", () => {
  it("parses a valid reference row", () => {
    const profiles = parseReferenceProfiles(
      `${HEADER}\nExample,21st century,Thinker,France,Liberalism,1.2,-0.4,high,21st century,Thinker,female,Note,https://example.test,true`,
    );
    expect(profiles).toHaveLength(1);
    expect(profiles[0]).toMatchObject({ name: "Example", x: 1.2, y: -0.4 });
  });

  it("rejects missing columns and invalid coordinates", () => {
    expect(() => parseReferenceProfiles("name,x,y\nExample,1,2")).toThrow(
      /Colonnes CSV manquantes/,
    );
    expect(() =>
      parseReferenceProfiles(
        `${HEADER}\nExample,21st century,Thinker,France,Liberalism,nope,2,high,21st century,Thinker,male,Note,,true`,
      ),
    ).toThrow(/Coordonnées invalides/);
  });

  it("validates the complete repository dataset", async () => {
    const profiles = await loadReferenceProfiles();
    expect(profiles).toHaveLength(500);
    expect(new Set(profiles.map((profile) => profile.gender))).toEqual(
      new Set(["male", "female"]),
    );
  });
});
