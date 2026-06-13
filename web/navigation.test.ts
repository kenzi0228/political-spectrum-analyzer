import { describe, expect, it } from "vitest";
import { buildAppRoute, parseAppRoute } from "./navigation";

describe("application routes", () => {
  it("round-trips the view and selected profile", () => {
    const route = buildAppRoute("visualization", "profile with spaces");
    expect(parseAppRoute(route)).toEqual({
      view: "visualization",
      profileId: "profile with spaces",
    });
  });

  it("falls back to home for an unknown view", () => {
    expect(parseAppRoute("#/unknown?profile=test")).toEqual({
      view: "home",
      profileId: "test",
    });
  });
});
