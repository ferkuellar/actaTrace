# Phase 7 — Security and Access Control Hardening

## 1. Phase Objective

Phase 7 hardens ActaTrace security and access control for a hostile environment. The goal is to protect authentication, authorization, public verification, document access, audit records, blockchain anchoring, administrative actions, and sensitive operational data without weakening auditability.

ActaTrace remains an electoral traceability and citizen audit platform. PostgreSQL is the system of record. Blockchain stores only hashes and critical-event proofs. Documents stay outside blockchain and are verified through SHA-256.

Out of scope:

- Electronic voting.
- Vote casting.
- Voter identity management.
- Blockchain identity wallet login.
- Zero-knowledge proofs.
- Kubernetes, service mesh, or SIEM integration.

## 2. Security Principles

- Least privilege by default.
- Deny by default.
- Every endpoint has an authorization rule.
- Every business-state change generates an audit event.
- Public endpoints must be explicitly public-safe.
- Secrets are environment-based and never stored in code.
- No sensitive data is stored on blockchain.
- Raw storage paths are not exposed to public users.
- Logs must not contain passwords, tokens, secrets, private keys, or raw storage internals.
- Audit logs are append-only at the application layer.
- Failed access attempts are recorded as security audit events.

## 3. Authentication Model

Implemented:

- JWT access tokens.
- bcrypt password hashing through Passlib.
- JWT expiration.
- JWT issuer validation.
- JWT audience validation.
- Account status validation.
- Secure generic login failure response.
- Failed login security audit events.
- Password policy validation on admin registration.
- `GET /api/v1/auth/me`.
- `POST /api/v1/auth/logout`.

JWT claims:

- `sub`
- `email`
- `role`
- `organization`
- `status`
- `iat`
- `exp`
- `iss`
- `aud`

Endpoints:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/register-admin`

Refresh token design is documented as a future extension and not enabled in this phase.

## 4. RBAC Model

Roles:

- `ADMIN_ELECTORAL`
- `CAPTURISTA`
- `SUPERVISOR`
- `AUDITOR`
- `OBSERVADOR`
- `CIUDADANO_PUBLICO`

Role permissions:

| Role | Access |
| --- | --- |
| `ADMIN_ELECTORAL` | Full system administration, user management, actas, documents, custody, PREP, alerts, audit review, blockchain anchoring. |
| `CAPTURISTA` | Create actas, upload/register documents, create PREP results, view own records. |
| `SUPERVISOR` | Review, approve, reject, validate custody, resolve alerts, anchor approved hashes. |
| `AUDITOR` | Read audit logs, traceability reports, forensic reports, alerts, and verification proofs. Cannot modify business records except explicitly allowed audit review notes. |
| `OBSERVADOR` | Read-only institutional access to non-sensitive dashboards and traceability views. |
| `CIUDADANO_PUBLICO` | Public-safe verification endpoints only. No admin API access. |

Implemented:

- Reusable `require_roles(*roles)` dependency.
- Forbidden access records `AUTH_FORBIDDEN`.
- Unauthorized access records `AUTH_UNAUTHORIZED`.
- Permission catalog in `app/core/permissions.py`.

## 5. Endpoint Security Matrix

| Endpoint group | Method(s) | Purpose | Auth | Allowed roles | Sensitive risk | Audit | Rate limit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/auth/login` | POST | Login | No | Public credential submitter | Brute force, credential stuffing | Yes | Strict |
| `/auth/logout` | POST | Logout | Yes | Active users | Token misuse | Yes | Monitored |
| `/auth/me` | GET | Current user | Yes | Active users | User metadata | No state change | Monitored |
| `/auth/register-admin` | POST | Initial admin registration | No in Phase 2 pattern | Bootstrap only | Admin creation abuse | Yes recommended | Strict |
| `/users/*` | GET/POST/PATCH/DELETE | User administration | Yes | `ADMIN_ELECTORAL` | PII, privilege changes | Yes for writes | Monitored |
| `/actas/*` | GET/POST/PATCH/actions | Acta operations | Yes | Capturista, Supervisor, Auditor, Observador by route | Electoral evidence metadata | Yes for writes/review | Monitored |
| `/documents/*` | GET/POST/download/verify | Document metadata, upload, integrity, download | Mixed | Admin, Capturista, Supervisor, Auditor; public only when explicitly safe | Storage paths, files | Yes | Download strict |
| `/custody-events/*` | GET/POST | Chain of custody | Yes | Supervisor, Auditor, Capturista where allowed | Custody responsibility | Yes | Monitored |
| `/prep-results/*` | GET/POST/validate | PREP capture/validation | Yes | Capturista, Supervisor, Auditor | Result mismatch data | Yes | Monitored |
| `/blockchain/anchor/*` | POST | Anchor hashes/events | Yes | Admin, Supervisor, Auditor | Wrong hash anchoring | Yes | Strict |
| `/blockchain/verify/hash/*` | GET | Verify public proof | No/controlled public | Public-safe | Enumeration | No state change | Moderate |
| `/traceability/actas/*` | GET | Timeline/report | Yes | Supervisor, Auditor, Observador where allowed | Internal traceability | Read audit recommended | Monitored |
| `/traceability/audit-events` | GET | Audit search | Yes | Admin, Auditor/Supervisor currently | Audit metadata | Read audit recommended | Monitored |
| `/traceability/public/actas/*` | GET | Public-safe timeline | No | Public | Public enumeration | No state change | Moderate |
| `/alerts/*` | GET/PATCH | Alert review/assignment/resolution | Yes | Admin, Supervisor, Auditor | Security/operational findings | Yes for actions | Monitored |
| `/public/*` | GET | Public search contract | No | Public | Enumeration/scraping | No state change | Moderate |

## 6. Data Protection

### 6.1 Encryption in Transit

Production requirements:

- HTTPS only.
- HSTS enabled at edge or API layer.
- No mixed content.
- CORS restricted to approved portal origins.

### 6.2 Encryption at Rest

Production requirements:

- PostgreSQL disk encryption.
- S3/MinIO server-side encryption.
- Encrypted backups.
- Secret manager for JWT secrets, S3 keys, Fabric identities, and database credentials.

### 6.3 Sensitive Data Handling

Implemented:

- Passwords are hashed, never stored plaintext.
- Sensitive audit state fields are masked.
- Storage keys and paths are treated as sensitive.
- JWT secrets remain environment-based.

Sensitive fields:

- passwords
- password hashes
- access/refresh tokens
- JWTs
- secrets
- private keys
- storage paths
- storage keys
- storage URLs

## 7. Audit Protection

Implemented:

- Application-level append-only `AuditLog` policy.
- No update/delete API endpoints for audit logs.
- Failed login events are recorded.
- Forbidden and unauthorized access attempts are recorded.
- Audit events include request ID.
- Correlation ID is added in request context.

Recommended for production:

- PostgreSQL triggers rejecting `UPDATE` and `DELETE` on `audit_logs`.
- Separate app DB user from migration DB user.
- Optional hash chain columns in a future migration.
- Optional blockchain anchoring for audit checkpoints.
- External append-only log archival.

## 8. Tamper-Evident Audit Hash Chain

Designed in `AuditHashChainService`.

Hash rules:

- Canonical JSON.
- Sorted keys.
- Volatile fields removed.
- Sensitive fields masked.
- SHA-256.
- Lowercase hex.

Future database fields:

- `event_hash`
- `previous_event_hash`
- `hash_algorithm`
- `hash_chain_sequence`

Purpose:

- Detect audit manipulation.
- Support forensic review.
- Support future blockchain anchoring of audit checkpoints.

## 9. Threat Model

### 9.1 Internal Manipulation

Threats:

- Capturista modifies acta after upload.
- Supervisor approves invalid acta.
- Admin disables audit controls.
- Insider attempts to delete audit records.

Mitigations:

- RBAC.
- Immutable audit logs.
- Before/after state capture.
- Approval workflows.
- Alert generation.
- Optional blockchain anchoring.

### 9.2 Data Tampering

Threats:

- Uploaded document replaced in storage.
- Database hash modified.
- Blockchain proof mismatch.
- PREP result changed after validation.

Mitigations:

- SHA-256 verification.
- Storage immutability recommendation.
- Database constraints.
- Integrity re-verification endpoints.
- Critical mismatch alerts.

### 9.3 Unauthorized Access

Threats:

- Stolen token.
- Weak password.
- Public endpoint abuse.
- Role escalation attempt.

Mitigations:

- Token expiration.
- Issuer/audience validation.
- Password policy.
- Least privilege.
- Rate limiting.
- Security audit events.

### 9.4 API Abuse

Threats:

- Brute force login.
- Enumeration of acta codes.
- Mass document download.
- Public verification scraping.

Mitigations:

- Rate limiting.
- Pagination limits.
- Public-safe response contracts.
- Download authorization.
- Request logging.

### 9.5 Blockchain Misuse

Threats:

- Anchoring wrong hash.
- Duplicate anchoring.
- Provider unavailable.
- Fabric identity compromise.

Mitigations:

- Role-restricted anchoring.
- Duplicate detection.
- Provider failure handling.
- Fabric identity management.
- Audit link for every transaction.

## 10. Security Controls Implemented

- JWT issuer and audience validation.
- JWT claims enriched with role, organization, status, email, issued-at, expiration.
- Password policy validation for admin registration.
- `/auth/me`.
- `/auth/logout`.
- Failed login audit event.
- Forbidden/unauthorized audit event.
- Security headers middleware.
- In-memory rate limiting middleware for local/single-process deployments.
- Sensitive data masking helper.
- Permission catalog.
- Audit hash chain design helper.
- Correlation ID propagation.

## 11. Security Headers

Implemented secure API defaults:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Strict-Transport-Security` when the request scheme is HTTPS.

## 12. Rate Limiting

Implemented in-memory limiter:

- Login: strict.
- Public search: moderate.
- Public hash verification: moderate.
- Document download: strict.
- Blockchain anchoring: strict.

Environment variables:

```env
RATE_LIMIT_LOGIN_PER_MINUTE=5
RATE_LIMIT_PUBLIC_SEARCH_PER_MINUTE=60
RATE_LIMIT_PUBLIC_VERIFY_PER_MINUTE=60
RATE_LIMIT_DOCUMENT_DOWNLOAD_PER_MINUTE=20
RATE_LIMIT_BLOCKCHAIN_ANCHOR_PER_MINUTE=10
```

Production note: replace in-memory rate limiting with Redis or edge gateway enforcement before horizontal scaling.

## 13. Security Events

Defined required events:

- `AUTH_LOGIN_SUCCESS`
- `AUTH_LOGIN_FAILED`
- `AUTH_LOGOUT`
- `AUTH_TOKEN_REFRESHED`
- `AUTH_FORBIDDEN`
- `AUTH_UNAUTHORIZED`
- `USER_CREATED`
- `USER_ROLE_CHANGED`
- `USER_DISABLED`
- `DOCUMENT_ACCESS_DENIED`
- `AUDIT_LOG_TAMPER_ATTEMPT`
- `BLOCKCHAIN_ANCHOR_REQUESTED`
- `BLOCKCHAIN_ANCHOR_FAILED`
- `PUBLIC_RATE_LIMIT_EXCEEDED`
- `SUSPICIOUS_ACCESS_DETECTED`

Implemented in this phase:

- `AUTH_LOGIN_SUCCESS`
- `AUTH_LOGIN_FAILED`
- `AUTH_LOGOUT`
- `AUTH_FORBIDDEN`
- `AUTH_UNAUTHORIZED`

## 14. Database Security Updates

Recommended:

- Restrict app DB user privileges.
- Use a separate migration DB user.
- Prevent `audit_logs` update/delete through triggers.
- Index security event fields.
- Use row-level security only if justified later.
- Encrypt backups.
- Test backup restores regularly.

Optional trigger design:

```sql
CREATE OR REPLACE FUNCTION prevent_audit_log_update()
RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'audit_logs are append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_logs_no_update
BEFORE UPDATE ON audit_logs
FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_update();

CREATE TRIGGER audit_logs_no_delete
BEFORE DELETE ON audit_logs
FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_update();
```

## 15. Implementation Architecture

Added or updated:

```text
app/core/security.py
app/core/permissions.py
app/core/rate_limit.py
app/core/masking.py
app/middleware/security_headers.py
app/middleware/rate_limit.py
app/middleware/request_context.py
app/services/auth_service.py
app/services/permission_service.py
app/services/security_audit_service.py
app/services/audit_hash_chain_service.py
app/api/v1/auth.py
app/tests/test_security_phase7.py
```

## 16. Input Validation and Error Handling

Validated or designed:

- Email.
- Password strength.
- UUIDs through route/schema usage.
- Role values through enums.
- SHA-256 hashes in existing verification paths.
- Public search inputs in frontend and future backend route.
- Safe structured errors.

Error codes:

- `AUTH_INVALID_CREDENTIALS`
- `AUTH_TOKEN_INVALID`
- `AUTH_FORBIDDEN`
- `AUTH_ACCOUNT_DISABLED`
- `SECURITY_RATE_LIMIT_EXCEEDED`
- `AUTH_PASSWORD_POLICY_FAILED`
- `SECURITY_AUDIT_TAMPER_ATTEMPT`
- `SECURITY_PUBLIC_DATA_VIOLATION`

## 17. Environment Variables

Added:

```env
JWT_ISSUER=actatrace
JWT_AUDIENCE=actatrace-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_SPECIAL=true
CORS_ALLOWED_ORIGINS=http://localhost:3010,http://localhost:3000
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
RATE_LIMIT_LOGIN_PER_MINUTE=5
RATE_LIMIT_PUBLIC_SEARCH_PER_MINUTE=60
RATE_LIMIT_PUBLIC_VERIFY_PER_MINUTE=60
RATE_LIMIT_DOCUMENT_DOWNLOAD_PER_MINUTE=20
RATE_LIMIT_BLOCKCHAIN_ANCHOR_PER_MINUTE=10
ENABLE_AUDIT_HASH_CHAIN=true
```

## 18. Tests

Added tests for:

- JWT required claims.
- Failed login security audit event.
- Disabled account login rejection.
- Invalid token rejection.
- `/auth/me`.
- `/auth/logout`.
- Security headers.
- Forbidden RBAC audit event.
- Public endpoint access without auth.
- Rate limit structured error.
- Password hashing.

Validation result:

```text
46 passed
```

## 19. Production Hardening Checklist

- HTTPS enabled.
- CORS restricted.
- Strong JWT secret configured.
- JWT issuer and audience configured.
- Database backups encrypted.
- Object storage encryption enabled.
- Secrets stored in secret manager.
- Audit log tamper protection enabled at database level.
- Rate limiting enabled at edge or Redis-backed middleware.
- Security headers enabled.
- Admin accounts reviewed.
- Default users removed.
- Error traces disabled.
- Logs reviewed for sensitive leakage.
- Dependency scan completed.
- Container image scan completed.
- Backup restore test completed.
- Fabric identities stored outside application code.

## 20. Known Limitations

- Rate limiting is in-memory and must be replaced for multi-process or multi-node deployments.
- Refresh tokens are designed but not implemented.
- Audit hash chain fields are designed but not migrated into the database yet.
- Database-level audit immutability trigger is recommended but not applied in this phase.
- Public search backend endpoint remains a contract from Phase 6.
- Account lockout is recommended but not yet implemented.

## 21. Phase Gate

Gate ID: `phase-7-security-access-control`

Status: Passed for implemented controls.

Evidence:

- JWT claims validation test.
- Failed login audit test.
- RBAC forbidden audit test.
- Security headers test.
- Rate limit test.
- Full backend suite: `46 passed`.

Risks:

- In-memory rate limiting is not production-sufficient.
- Database triggers are still pending.
- Refresh token lifecycle is not implemented.

Required corrections before production:

- Add DB-level audit immutability.
- Move rate limits to Redis or gateway.
- Configure production-grade secrets and CORS.

## 22. Phase 8 Recommendation

Recommended next phase:

**Phase 8 — Observability and Monitoring**

Phase 8 should build:

- Structured logs.
- Metrics.
- Health checks.
- Audit dashboards.
- Security event monitoring.
- Alerting rules.
- Operational dashboards.
- Incident response visibility.
