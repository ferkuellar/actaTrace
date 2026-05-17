# Phase 2 — Backend API Foundation

## 1. Phase Objective

Phase 2 builds the backend API foundation for ActaTrace using FastAPI. The goal is a clean, modular, locally runnable API that supports institutional workflows for electoral evidence traceability without introducing frontend, production blockchain integration, or electronic voting.

The API supports:

- Acta registration.
- Document metadata registration.
- SHA-256 hash generation.
- Chain-of-custody events.
- PREP result capture and validation.
- User management.
- Audit logging.
- Basic role-based access control.

## 2. Implementation Summary

The backend was created under `actatrace-backend/` as a modular monolith. Controllers are thin FastAPI routers. Business rules live in services. Database access is isolated in repositories. SQLAlchemy models define the Phase 1 domain schema. Audit events are emitted by services for create, update, verification, and mismatch operations.

PostgreSQL remains the system of record. Blockchain is not integrated in Phase 2; only the `BlockchainAnchor` model exists so future anchoring can be added without changing the core domain model.

## 3. Technology Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Pydantic v2
- Uvicorn
- python-jose
- passlib/bcrypt
- Standard structured logging
- pytest

## 4. API Surface

Base path: `/api/v1`

Implemented endpoints:

- `GET /health`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register-admin`
- `GET /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `POST /api/v1/users`
- `PATCH /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`
- `GET /api/v1/actas`
- `GET /api/v1/actas/{acta_id}`
- `POST /api/v1/actas`
- `PATCH /api/v1/actas/{acta_id}`
- `POST /api/v1/actas/{acta_id}/verify-hash`
- `POST /api/v1/actas/{acta_id}/submit-review`
- `POST /api/v1/actas/{acta_id}/approve`
- `POST /api/v1/actas/{acta_id}/reject`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `POST /api/v1/documents/register-metadata`
- `POST /api/v1/documents/{document_id}/verify-integrity`
- `GET /api/v1/custody-events`
- `GET /api/v1/custody-events/{event_id}`
- `POST /api/v1/custody-events`
- `GET /api/v1/actas/{acta_id}/custody-timeline`
- `GET /api/v1/prep-results`
- `GET /api/v1/prep-results/{prep_result_id}`
- `POST /api/v1/prep-results`
- `POST /api/v1/prep-results/{prep_result_id}/validate`
- `GET /api/v1/actas/{acta_id}/prep-results`

## 5. RBAC

RBAC is implemented through the reusable dependency `require_roles(*roles)`.

Role rules:

- `ADMIN_ELECTORAL`: full system access.
- `CAPTURISTA`: create actas, register document metadata, create custody events, create PREP results.
- `SUPERVISOR`: review, approve, reject, verify, and validate operational records.
- `AUDITOR`: read institutional data and perform verification-oriented operations.
- `OBSERVADOR`: read-only institutional access.
- `CIUDADANO_PUBLICO`: no admin API access in Phase 2.

## 6. Auditability

The backend includes:

- `AuditLog` SQLAlchemy model.
- `AuditService`.
- Request ID middleware.
- Structured request logging middleware.
- Audit event emission from business services.

Audit events are created for:

- User creation/update/deactivation.
- Document registration.
- Document integrity verification.
- Document hash mismatch.
- Acta creation/update.
- Acta hash verification.
- Acta review submission, approval, and rejection.
- Custody event creation.
- PREP result creation.
- PREP validation and mismatch detection.

No update or delete endpoints are exposed for audit logs.

## 7. Local Run

```bash
cd actatrace-backend
cp .env.example .env
docker compose up --build
```

Apply migrations after generating the first migration:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

API documentation is available at:

```text
http://localhost:8000/docs
```

## 8. Tests

Run:

```bash
cd actatrace-backend
pytest
```

Implemented test coverage:

- Health endpoint.
- SHA-256 generation and verification.
- RBAC forbidden access.
- Acta creation.
- Audit log creation.
- PREP validation happy path.

## 9. Security Notes

- Passwords are hashed with bcrypt.
- JWT access tokens are signed with an environment-provided secret.
- No credentials are hardcoded.
- CORS is environment-configurable.
- Public citizen endpoints are intentionally deferred.
- Document contents are not logged.
- Real file storage is deferred; Phase 2 registers metadata and hashes only.

## 10. Known Limitations

- No production blockchain provider is integrated.
- No real object storage provider is integrated.
- No frontend is included.
- No public citizen verification API is included yet.
- No refresh tokens or MFA are included yet.
- Alembic migration files are not pre-generated; the project is configured for autogeneration.
- Tests use SQLite dependency overrides; deployment uses PostgreSQL.

## 11. Anti-Overengineering Guardrails

Phase 2 intentionally excludes:

- Microservices.
- Kafka.
- Event sourcing.
- AI fraud detection.
- Electronic voting.
- Vote casting.
- Complex smart contracts.
- Production blockchain integration.
- Real object storage integration.
- Kubernetes.

## 12. Phase 3 Recommendation

The next phase should be:

**Phase 3 — Blockchain Verification Layer**

Phase 3 should add:

- Blockchain provider interface.
- Blockchain facade.
- Local mock blockchain provider.
- Optional testnet provider.
- Hash anchoring workflow.
- Verification endpoint.

Phase 3 must keep PostgreSQL as the system of record. Blockchain must remain a verification layer, not a database.
