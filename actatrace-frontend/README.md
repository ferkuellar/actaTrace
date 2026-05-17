# ActaTrace Citizen Verification Portal

Public-facing Next.js portal for citizen verification of electoral evidence records.

## Scope

This frontend supports:

- Home page with public verification explanation.
- Search by acta code or polling station code.
- Public acta detail page.
- Document fingerprint verification.
- Public-safe traceability timeline.
- Citizen-friendly proof language.

It intentionally excludes electronic voting, vote casting, public accounts, wallet login, token language, and admin dashboards.

## Local Setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open:

```text
http://localhost:3000
```

Backend default:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Tests

```bash
npm run test:e2e
```

## Public API Contracts

Used endpoints:

- `GET /api/v1/traceability/public/actas/{acta_code}`
- `GET /api/v1/blockchain/verify/hash/{hash_value}`
- `GET /api/v1/public/search`
- `GET /api/v1/documents/{document_id}/download`

Backend TODO:

- Implement `GET /api/v1/public/search`.
- Ensure document downloads enforce `PUBLIC_VERIFIABLE`.
- Consider a dedicated public acta summary endpoint to reduce frontend derivation.

## Privacy

The UI does not render internal user IDs, emails, IP addresses, raw user agents, raw storage paths, request IDs, private notes, or sensitive metadata.
