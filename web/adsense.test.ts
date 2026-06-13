// @vitest-environment node

import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const publisherId = "ca-pub-8513561134992486";

describe("AdSense publication contract", () => {
  it("declares the publisher account and gates the official script behind consent", () => {
    const html = readFileSync("index.html", "utf8");
    const loader = readFileSync("web/ads.ts", "utf8");

    expect(html).toContain(`name="google-adsense-account"`);
    expect(html).toContain(`content="${publisherId}"`);
    expect(html).not.toContain(
      `pagead/js/adsbygoogle.js?client=${publisherId}`,
    );
    expect(loader).toContain(`pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=`);
    expect(loader).toContain("script.crossOrigin = \"anonymous\"");
  });

  it("publishes the authorized seller declaration", () => {
    const adsText = readFileSync("public/ads.txt", "utf8").trim();

    expect(adsText).toBe(
      "google.com, pub-8513561134992486, DIRECT, f08c47fec0942fa0",
    );
  });
});
