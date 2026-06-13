import { describe, expect, it } from "vitest";

const relativeLuminance = (hex: string): number => {
  const channels = hex
    .replace("#", "")
    .match(/.{2}/g)
    ?.map((channel) => Number.parseInt(channel, 16) / 255);
  if (!channels) throw new Error(`Invalid color: ${hex}`);
  const [red, green, blue] = channels.map((channel) =>
    channel <= 0.03928
      ? channel / 12.92
      : ((channel + 0.055) / 1.055) ** 2.4,
  );
  return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
};

const contrastRatio = (foreground: string, background: string): number => {
  const lighter = Math.max(relativeLuminance(foreground), relativeLuminance(background));
  const darker = Math.min(relativeLuminance(foreground), relativeLuminance(background));
  return (lighter + 0.05) / (darker + 0.05);
};

describe("essential text contrast", () => {
  it.each([
    ["dark primary text", "#fafafa", "#0e1117"],
    ["dark secondary text", "#b8bccb", "#0e1117"],
    ["light primary text", "#111827", "#f5f7fb"],
    ["light secondary text", "#4b5563", "#f5f7fb"],
  ])("%s meets WCAG AA for normal text", (_name, foreground, background) => {
    expect(contrastRatio(foreground, background)).toBeGreaterThanOrEqual(4.5);
  });
});
