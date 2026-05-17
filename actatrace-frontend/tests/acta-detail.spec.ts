import { expect, test } from "@playwright/test";

test("acta detail loads public-safe timeline", async ({ page }) => {
  await page.route("**/api/v1/traceability/public/actas/ACTA-1", async (route) => {
    await route.fulfill({
      json: [
        {
          acta_code: "ACTA-1",
          polling_station_code: "MXCMX-D12-S0456-B01",
          event_type: "DOCUMENT_RETRIEVED",
          timestamp: "2026-05-17T10:00:00Z",
          verification_status: "RECORDED",
          severity: "INFO",
          hash_proof: { hash_value: "a".repeat(64) },
          public_document_status: "PUBLIC_VERIFIABLE",
          blockchain_anchor_proof: { anchor_id: "anchor-1" }
        }
      ]
    });
  });
  await page.goto("/actas/ACTA-1");
  await expect(page.getByRole("heading", { name: "ACTA-1" })).toBeVisible();
  await expect(page.getByText(/public traceability timeline/i)).toBeVisible();
  await expect(page.getByText(/sensitive internal details are not shown/i)).toBeVisible();
});

test("sensitive fields are not rendered in public acta detail", async ({ page }) => {
  await page.route("**/api/v1/traceability/public/actas/ACTA-2", async (route) => {
    await route.fulfill({
      json: [
        {
          acta_code: "ACTA-2",
          polling_station_code: "MXCMX-D12-S0456-B01",
          event_type: "DOCUMENT_RETRIEVED",
          timestamp: "2026-05-17T10:00:00Z",
          verification_status: "RECORDED",
          severity: "INFO",
          ip_address: "127.0.0.1",
          actor_user_id: "internal-user",
          hash_proof: { hash_value: "b".repeat(64) },
          public_document_status: "PUBLIC_VERIFIABLE",
          blockchain_anchor_proof: {}
        }
      ]
    });
  });
  await page.goto("/actas/ACTA-2");
  await expect(page.getByText("127.0.0.1")).toHaveCount(0);
  await expect(page.getByText("internal-user")).toHaveCount(0);
});
