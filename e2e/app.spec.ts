import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Refuser" }).click();
});

test("creates a profile and reaches its explainable analysis", async ({ page }) => {
  await page.getByRole("button", { name: "Saisie" }).click();
  await page.getByLabel("Capitalisme").fill("72");
  await page.getByLabel("Régulation").fill("35");
  await page.getByRole("button", { name: "Se rendre à l’analyse" }).click();

  await expect(page).toHaveURL(/\/analysis\?profile=/);
  await expect(page.getByRole("heading", { name: /Analyse de/ })).toBeVisible();
  await expect(page.getByText(/Cette lecture est heuristique/)).toBeVisible();
});

test("serves direct real routes and the methodology status", async ({ page }) => {
  await page.goto("/methodology");
  await expect(page).toHaveURL(/\/methodology/);
  await expect(page.getByRole("heading", { name: "Méthodologie" })).toBeVisible();
  await expect(page.getByText(/modèle heuristique éditorial/)).toBeVisible();
});

test("loads the complete reference atlas lazily", async ({ page }) => {
  await page.getByRole("button", { name: "Atlas" }).click();
  await expect(page.getByText("500 / 500")).toBeVisible();
  await page.getByText("Karl Marx").click();
  await expect(page.getByText("Non sourcé · à vérifier")).toBeVisible();
});

test("has no serious automated accessibility violation on home", async ({ page }) => {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(results.violations.filter((violation) => violation.impact === "serious" || violation.impact === "critical")).toEqual([]);
});
