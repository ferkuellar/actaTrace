import { expect, test } from "@playwright/test";

test("hash verification success", async ({ page }) => {
  const hash = "a".repeat(64);
  await page.route(`**/api/v1/blockchain/verify/hash/${hash}`, async (route) => {
    await route.fulfill({
      json: {
        exists: true,
        hash_value: hash,
        entity_id: "ACTA-1",
        transaction_hash: "proof-reference-1",
        anchored_at: "2026-05-17T10:00:00Z",
        verification_status: "VERIFIED"
      }
    });
  });
  await page.goto("/verify");
  await page.getByLabel("Document fingerprint").fill(hash);
  await page.getByRole("button", { name: /verify fingerprint/i }).click();
  await expect(page.getByRole("heading", { name: /fingerprint found/i })).toBeVisible();
});

test("hash verification validates input", async ({ page }) => {
  await page.goto("/verify");
  await page.getByLabel("Document fingerprint").fill("bad-hash");
  await page.getByRole("button", { name: /verify fingerprint/i }).click();
  await expect(page.getByText(/valid 64-character document fingerprint/i)).toBeVisible();
});
