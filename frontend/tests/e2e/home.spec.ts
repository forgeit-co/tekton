import { expect, test } from "@playwright/test";

test("home route displays the localized home heading", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: "Build your home, one step at a time" }),
  ).toBeVisible();
});
