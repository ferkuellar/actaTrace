import { expect, test } from "@playwright/test";

test("home page renders citizen verification entry points", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /verify electoral evidence/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /search public records/i })).toBeVisible();
  await expect(page.getByText(/does not count votes/i)).toBeVisible();
});

test("search form validates required input", async ({ page }) => {
  await page.goto("/search");
  await page.getByRole("button", { name: /^search$/i }).click();
  await expect(page.getByText(/enter an acta code or polling station code/i)).toBeVisible();
});

test("search by acta code calls public search contract", async ({ page }) => {
  await page.route("**/api/v1/public/search?acta_code=ACTA-1", async (route) => {
    await route.fulfill({
      json: [
        {
          acta_code: "ACTA-1",
          polling_station_code: "MXCMX-D12-S0456-B01",
          municipality: "Benito Juarez",
          district: "D12",
          verification_status: "PARTIALLY_VERIFIED",
          document_integrity_status: "VERIFIED",
          prep_validation_status: "REQUIRES_REVIEW",
          last_verified_at: "2026-05-17T10:00:00Z"
        }
      ]
    });
  });
  await page.goto("/search");
  await page.getByLabel("Acta code").fill("ACTA-1");
  await page.getByRole("button", { name: /^search$/i }).click();
  await expect(page.getByRole("link", { name: "ACTA-1" })).toBeVisible();
});
