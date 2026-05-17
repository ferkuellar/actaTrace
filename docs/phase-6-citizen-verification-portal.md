# Phase 6 — Citizen Verification Portal

## 1. Phase Objective

Phase 6 creates the public-facing ActaTrace portal for citizen verification of electoral evidence records. The portal helps non-technical users search actas, review public-safe traceability, understand verification status, and verify document fingerprints against public proof records.

The portal supports:

- Public search by polling station.
- Public search by acta code.
- Acta verification detail page.
- Hash verification result, described as a document fingerprint.
- Independent verification proof display.
- Public-safe traceability timeline.
- Clear explanation of verification status.
- Institutional, clean, trust-oriented UI.

It does not implement electronic voting, vote casting, wallet login, public user accounts, or admin dashboards.

## 2. Core UX Principle

The portal answers:

> Can this acta and its result be verified with evidence?

Citizens should understand:

- What acta is being shown.
- Whether the document is intact.
- Whether the result matches the registered evidence.
- Whether the document fingerprint has independent proof.
- What public traceability events happened.
- Whether there are public inconsistencies or review notices.

## 3. Target Users

The portal is designed for:

- General citizens.
- Journalists.
- Civic observers.
- Political party observers.
- Academic auditors.
- Electoral institution staff using the public view.

The language assumes many users are not technical.

## 4. Design Language

The UI uses an institutional style:

- Clean layout.
- Strong typography.
- High contrast.
- Calm green, slate, white, and review-state colors.
- Clear status indicators.
- Minimal animation.
- No crypto aesthetic.
- No trading or web3 visuals.
- No wallet or token language.

Tone is clear, neutral, evidence-based, non-partisan, and understandable.

## 5. Technology Stack

Implemented stack:

- React + Vite.
- React.
- TypeScript.
- Tailwind CSS.
- Lucide icons.
- Native `fetch`.
- Zod response validation.
- Playwright E2E tests.

The UI follows shadcn-style component discipline without requiring a generated shadcn registry in Phase 6.

## 6. Frontend Structure

Implemented structure:

```text
actatrace-frontend/
├── src/
│   ├── main.tsx
│   ├── styles.css
│   └── vite-env.d.ts
├── tests/
├── .env.example
├── index.html
├── package.json
├── vite.config.ts
└── README.md
```

The first implementation attempt used Next.js, but the local environment runs Node 24 and repeatedly failed inside Next's Windows file handling. The accepted implementation uses React + Vite to keep the portal simple, stable, and production-buildable.

## 7. Pages

### 7.1 Home Page

Route: `/`

Includes:

- Headline: “Verify electoral evidence with traceable records.”
- Short explanation.
- Search entry point.
- Three-step verification explanation.
- Trust banner.
- Disclaimer that the portal verifies evidence records and does not replace the official electoral authority.

### 7.2 Search Page

Route: `/search`

Supports:

- Search by acta code.
- Search by polling station code.
- User-friendly error state if the public search endpoint is unavailable.

Expected result fields:

- `acta_code`
- `polling_station_code`
- `municipality`
- `district`
- `verification_status`
- `document_integrity_status`
- `prep_validation_status`
- `last_verified_at`

### 7.3 Acta Detail Page

Route: `/actas/[actaCode]`

Shows:

- Acta summary.
- Polling station code.
- Overall verification status.
- Document proof card.
- PREP comparison card.
- Independent verification proof card.
- Public-safe traceability timeline.
- Public review notice when review events are present.

Sensitive fields are not rendered.

### 7.4 Verification Page

Route: `/verify`

Supports:

- Paste 64-character document fingerprint.
- Validate format before API call.
- Verify against public proof API.
- Show found/not found result.
- Show linked public acta if available.
- Show proof reference and anchored timestamp if available.

### 7.5 About Page

Route: `/about`

Explains:

- What ActaTrace verifies.
- What it does not verify.
- How document fingerprints work.
- Why files are not stored in proof records.
- How public traceability works.
- System limits.

## 8. API Integration

Used public-safe endpoints:

- `GET /api/v1/traceability/public/actas/{acta_code}`
- `GET /api/v1/blockchain/verify/hash/{hash_value}`
- `GET /api/v1/public/search?acta_code=&polling_station_code=&municipality=&district=&status=`
- `GET /api/v1/documents/{document_id}/download`

Backend TODOs:

- Implement `GET /api/v1/public/search`.
- Add a dedicated `GET /api/v1/public/actas/{acta_code}` summary endpoint to avoid deriving summary status from timeline events.
- Ensure document download only returns files with `PUBLIC_VERIFIABLE` access status.
- Keep public responses redacted at the backend, not only the frontend.

## 9. TypeScript Types

Defined:

- `PublicActaSummary`
- `PublicPollingStation`
- `PublicVerificationStatus`
- `PublicTimelineEvent`
- `PublicDocumentProof`
- `PublicPrepResult`
- `PublicBlockchainProof`
- `PublicSearchResult`
- `HashVerificationResult`

## 10. Citizen Status Model

Document integrity:

- Verified.
- Not verified yet.
- Mismatch detected.
- Document unavailable.

PREP validation:

- Matches registered acta.
- Requires review.
- Mismatch detected.
- Not available.

Independent proof:

- Anchored.
- Pending.
- Not anchored.
- Verification failed.

Overall acta verification:

- Verified.
- Partially verified.
- Requires review.
- Inconsistency detected.
- Not available.

## 11. UX Copy Rules

Citizen-facing wording:

- “SHA-256 hash” becomes “document fingerprint.”
- “Blockchain anchor” becomes “independent verification proof.”
- “Transaction hash” becomes “proof reference.”
- “Audit log” becomes “traceability record.”

Technical details remain available through copyable proof values for auditors.

## 12. Core Components

Implemented:

- `PublicHeader`
- `PublicFooter`
- `TrustBanner`
- `ActaSearchForm`
- `PollingStationSearchForm`
- `SearchResults`
- `ActaSummaryCard`
- `VerificationStatusCard`
- `DocumentProofCard`
- `PrepResultCard`
- `BlockchainProofCard`
- `PublicTimeline`
- `HashVerificationForm`
- `VerificationResult`
- `EvidenceExplanation`
- `StatusBadge`
- `EmptyState`
- `ErrorState`
- `LoadingState`
- `CopyButton`

## 13. Accessibility

Implemented:

- Semantic headings and sections.
- Keyboard-accessible links, buttons, forms, and copy actions.
- Visible focus states.
- High contrast status badges.
- ARIA labels for form inputs.
- `aria-live` verification result updates.
- Responsive mobile layout.

## 14. Security and Privacy

Frontend rules:

- Never display internal user IDs.
- Never display emails.
- Never display IP addresses.
- Never display raw user agents.
- Never display storage paths.
- Never display private notes.
- Validate user inputs before API calls.
- Do not log search data to console.
- Use only `NEXT_PUBLIC_*` variables for browser-accessible configuration.

## 15. Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=ActaTrace
VITE_ENVIRONMENT=local
```

## 16. Error Handling

The UI includes friendly states for:

- No acta found.
- Invalid search.
- Verification service unavailable.
- Document unavailable.
- Hash not found.
- Public data unavailable.
- Network error.

Stack traces and raw API errors are not shown to citizens.

## 17. Testing

Created Playwright tests for:

- Home page rendering.
- Search form validation.
- Search by acta code.
- Acta detail loading timeline.
- Sensitive fields not rendered.
- Hash verification success.
- Hash verification invalid input.
- Mobile project configuration.

Run:

```bash
cd actatrace-frontend
npm install
npm run test:e2e
```

## 18. Known Limitations

- The backend public search endpoint is documented but not implemented yet.
- The acta detail page currently derives summary status from the public timeline response.
- Public document download UI is prepared through API contract, but document links should wait for backend access enforcement.
- No public rate limiter is implemented in the frontend; it must be enforced by backend or edge infrastructure.
- No admin dashboard or authenticated UI is included in this phase.

## 19. Anti-Overengineering Guardrails

Not added:

- Wallet login.
- Tokens.
- NFT certificates.
- Web3 branding.
- Complex animations.
- Real-time websockets.
- Public user accounts.
- Electronic voting UI.
- Vote casting UI.
- Admin dashboard.
- Political party branding.

## 20. Phase 7 Recommendation

Recommended next phase:

**Phase 7 — Security and Access Control Hardening**

Phase 7 should build:

- Stronger authentication.
- Role-based UI access.
- Admin session controls.
- Public API rate limiting.
- Security headers.
- Audit-safe access design.
- Threat model refinement.
