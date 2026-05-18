# Phase 10 — Validation, Testing, and Release Readiness

## 1. Phase Objective

Phase 10 defines and implements a complete validation strategy for ActaTrace.

The test strategy must prove:

- Actas can be registered correctly.
- Documents are hashed correctly.
- Modified documents are detected.
- Duplicate actas are detected.
- PREP mismatches are detected.
- Chain of custody is traceable.
- Audit logs are immutable.
- Blockchain anchors can be verified.
- Unauthorized access is blocked.
- Public endpoints expose only public-safe data.
- System failures are handled safely.

ActaTrace does not implement electronic voting. Phase 10 validates evidence traceability, auditability, integrity, and release readiness.

## 2. Testing Principles

- Test evidence, not assumptions.
- Every critical workflow must have happy-path and failure-path tests.
- Every business-state change must generate an audit event.
- Every integrity failure must create an alert.
- Every public endpoint must be checked for sensitive data leakage.
- Every role must be tested against allowed and forbidden actions.
- Blockchain must be mocked locally but behavior must be verifiable.
- Tests must simulate real-world failures, not only clean inputs.

## 3. Test Types Required

### 3.1 Unit Tests

Implemented under:

```text
actatrace-backend/tests/unit/
```

Coverage includes:

- Hash generation
- Canonical JSON hashing
- State transition validation
- RBAC permission checks
- Input validation
- Audit diff generation
- Sensitive field masking
- Object key generation
- File type validation contract

### 3.2 Integration Tests

Implemented under:

```text
actatrace-backend/tests/integration/
```

Coverage includes:

- API + database
- Document upload + storage
- Acta creation + document link
- PREP mismatch detection
- Custody event timeline
- Blockchain mock provider + database anchor
- Audit log creation
- Alert creation
- Public verification redaction

### 3.3 Audit Validation Tests

Audit tests validate:

- Audit log created on business actions
- Audit log includes before/after state where applicable
- Audit logs cannot be updated
- Audit logs cannot be deleted
- Tamper attempt is blocked
- Forensic report reconstructs acta lifecycle

### 3.4 Blockchain Verification Tests

Blockchain tests validate:

- Document hash anchor success
- Critical event hash design through canonical hashing
- Duplicate hash anchor rejected
- Hash verification success
- Hash verification not found
- Provider failure handled safely
- Failed provider creates failed anchor status
- Acta status updates only after successful anchor

### 3.5 Security Tests

Implemented under:

```text
actatrace-backend/tests/security/
```

Coverage includes:

- Login success
- Login failure
- Role escalation blocked
- Public user blocked from admin API
- Forbidden access creates security audit event
- Public responses are redacted
- Rate limit behavior

### 3.6 Observability Tests

Implemented under:

```text
actatrace-backend/tests/observability/
```

Coverage includes:

- `/health/ready`
- `/metrics`
- Hash mismatch metric
- Failed login metric through existing observability suite
- Structured logs include `request_id`
- Structured logs mask passwords and tokens

### 3.7 End-to-End Smoke Tests

Implemented under:

```text
actatrace-backend/tests/e2e/
```

Smoke flow:

1. Create users.
2. Login.
3. Create polling station.
4. Create acta.
5. Upload document.
6. Generate hash.
7. Anchor hash using mock blockchain.
8. Create PREP result.
9. Validate PREP.
10. Retrieve traceability timeline.
11. Generate forensic report.
12. Query public verification API.

## 4. Critical Test Scenarios

### 4.1 Modified Document

Scenario:

1. Upload acta document.
2. Generate and store SHA-256 hash.
3. Anchor hash to mock blockchain.
4. Replace or modify stored document content.
5. Run integrity verification.
6. System must detect mismatch.

Expected result:

- `document_integrity_status = MISMATCH`
- Alert created: `DOCUMENT_HASH_MISMATCH`
- Audit event created: `DOCUMENT_HASH_MISMATCH`
- Metric incremented: `document_hash_mismatches_total`
- Forensic report shows mismatch

### 4.2 Duplicate Acta

Scenario:

1. Create acta with `acta_code`.
2. Attempt to create another acta with the same `acta_code`.
3. Attempt to link same document hash to different acta.

Expected result:

- Duplicate acta rejected or flagged.
- Alert created: `DUPLICATE_ACTA` or `DUPLICATE_DOCUMENT_HASH`.
- Audit event created.
- `409 Conflict` returned where appropriate.

### 4.3 Mismatched PREP

Scenario:

1. Create acta with expected structured results.
2. Create PREP result with different totals.
3. Run PREP validation.

Expected result:

- `prep_validation_status = MISMATCHED`
- Alert created: `PREP_ACTA_MISMATCH`
- Audit event created
- Forensic report shows discrepancy

### 4.4 Custody Gap

Scenario:

1. Create custody transfer event.
2. Do not create corresponding received event.
3. Run inconsistency detection after threshold.

Expected result:

- Alert created: `CUSTODY_GAP`
- Severity is `WARNING` or `CRITICAL`
- Audit event created
- Timeline shows open transfer

### 4.5 Unauthorized State Transition

Scenario:

1. Attempt to move acta from `VERIFIED` back to `DRAFT`.
2. Attempt by unauthorized role.

Expected result:

- Transition rejected
- Security audit event created
- Alert created if suspicious
- `403` or `409` returned

### 4.6 Blockchain Provider Failure

Scenario:

1. Configure mock provider to fail.
2. Attempt to anchor document hash.
3. Verify database and audit behavior.

Expected result:

- Anchor status becomes `FAILED`
- Acta status does not become `ANCHORED`
- Audit event created: `BLOCKCHAIN_ANCHOR_FAILED`
- No corrupted state

### 4.7 Public Data Leakage

Scenario:

1. Call public acta verification endpoint.
2. Inspect response.

Response must not include:

- Internal user IDs
- Emails
- IP addresses
- Raw storage paths
- Private notes
- JWT data
- Request internals
- Sensitive metadata

## 5. Test Data Strategy

Fixtures provide realistic but fake electoral data:

- Admin user
- Capturista user
- Supervisor user
- Auditor user
- Observador user
- Public user context
- Polling station
- Acta
- Document
- Custody event
- PREP result
- Blockchain anchor
- Audit log
- Alert

No real voter data is used.

## 6. Test Environment

Primary local test stack:

- `pytest`
- FastAPI `TestClient`
- SQLite in-memory test database through dependency overrides
- Local storage provider
- Mock blockchain provider
- Temporary files for document tests

Optional Docker test profile:

```text
actatrace-backend/docker-compose.test.yml
```

Services:

- `test-postgres`
- `backend-test`

## 7. Test Directory Structure

Created:

```text
actatrace-backend/tests/
├── unit/
├── integration/
├── security/
├── observability/
├── e2e/
├── fixtures/
└── conftest.py
```

The existing `app/tests/` suite remains intact and continues to run as the regression suite.

## 8. Required Test Cases

### Unit Test Cases

| Test ID | Name | Purpose | Preconditions | Steps | Expected result | Severity if failed |
| --- | --- | --- | --- | --- | --- | --- |
| UT-001 | SHA-256 hash is deterministic | Prove same bytes always produce same hash. | HashService available. | Hash same content twice. | Hashes match. | Critical |
| UT-002 | Modified file produces different hash | Prove tamper evidence works. | HashService available. | Hash original and modified bytes. | Hashes differ. | Critical |
| UT-003 | Canonical JSON hash is deterministic | Prove event hash stability. | Canonical hash function available. | Hash same object with different key order. | Hashes match. | High |
| UT-004 | Invalid SHA-256 format rejected | Prevent invalid blockchain proofs. | BlockchainService available. | Validate invalid hash. | Error raised. | High |
| UT-005 | Forbidden role rejected | Prove RBAC boundaries. | Permission map loaded. | Check Capturista approval permission. | Permission denied. | Critical |
| UT-006 | Sensitive fields masked from audit state | Prevent leakage in audit state. | Masking helper available. | Mask token/password payload. | Sensitive values masked. | Critical |
| UT-007 | Invalid acta state transition rejected | Prevent lifecycle regression. | Acta lifecycle defined. | Check VERIFIED to DRAFT. | Transition not allowed. | High |
| UT-008 | Object key generated safely | Prevent unsafe storage paths. | DocumentStorageService available. | Generate key from unsafe components. | Key is sanitized. | High |

### Integration Test Cases

| Test ID | Name | Purpose | Preconditions | Steps | Expected result | Severity if failed |
| --- | --- | --- | --- | --- | --- | --- |
| IT-001 | Create acta successfully | Prove acta registration. | Capturista and polling station exist. | POST `/actas`. | Acta created and audit logged. | Critical |
| IT-002 | Upload document and store hash | Prove document evidence registration. | Acta exists. | Upload PDF. | Hash and metadata stored. | Critical |
| IT-003 | Verify document integrity success | Prove unchanged file verifies. | Document exists. | Recompute hash. | Integrity valid. | Critical |
| IT-004 | Detect modified document | Prove tamper detection. | Document exists. | Modify stored object and verify. | Mismatch detected. | Critical |
| IT-005 | Create custody event and timeline | Prove custody traceability. | Acta exists. | Create custody event and fetch timeline. | Timeline ordered. | High |
| IT-006 | Create PREP result | Prove PREP capture. | Acta exists. | POST PREP result. | PREP stored. | High |
| IT-007 | Detect PREP mismatch | Prove result discrepancy detection. | Acta and mismatched PREP exist. | Run detection. | Alert created. | Critical |
| IT-008 | Anchor document hash to mock blockchain | Prove proof anchoring workflow. | Document exists. | Anchor hash. | Mock transaction stored. | High |
| IT-009 | Generate forensic report | Prove reconstruction. | Acta lifecycle exists. | Fetch report. | Report has core sections. | Critical |
| IT-010 | Public acta verification returns redacted data | Prove public-safe API. | Public acta exists. | Fetch public timeline. | Sensitive fields absent. | Critical |

### Audit Test Cases

| Test ID | Name | Purpose | Expected result | Severity if failed |
| --- | --- | --- | --- | --- |
| AT-001 | Business action creates audit log | Prove every critical change records evidence. | AuditLog exists. | Critical |
| AT-002 | Audit log includes before/after state | Prove forensic context. | Changed fields captured. | High |
| AT-003 | Audit log update blocked | Prove immutability. | Update raises error. | Critical |
| AT-004 | Audit log delete blocked | Prove immutability. | Delete raises error. | Critical |
| AT-005 | Tamper attempt creates security event | Prove tamper evidence. | Security event exists. | Critical |
| AT-006 | Audit hash chain validates | Prove tamper-evident sequence. | Chain validates. | High |
| AT-007 | Forensic report reconstructs full lifecycle | Prove audit usability. | Report complete. | Critical |

### Blockchain Test Cases

| Test ID | Name | Purpose | Expected result | Severity if failed |
| --- | --- | --- | --- | --- |
| BT-001 | Anchor document hash success | Prove anchoring. | Anchor status `ANCHORED`. | High |
| BT-002 | Verify existing hash success | Prove verification. | `exists = true`. | High |
| BT-003 | Verify missing hash returns not found | Prove negative path. | `exists = false`. | Medium |
| BT-004 | Duplicate anchor rejected | Prevent duplicate proof. | Conflict raised. | High |
| BT-005 | Provider failure handled safely | Prevent corrupt state. | Anchor `FAILED`, audit logged. | Critical |
| BT-006 | Anchor linked to audit log | Prove audit linkage. | Audit event exists. | Critical |

### Security Test Cases

| Test ID | Name | Purpose | Expected result | Severity if failed |
| --- | --- | --- | --- | --- |
| ST-001 | Admin can manage users | Prove admin permission. | HTTP 200. | High |
| ST-002 | Capturista cannot approve acta | Prevent role escalation. | HTTP 403. | Critical |
| ST-003 | Auditor cannot modify business record | Enforce read-only audit role. | HTTP 403. | Critical |
| ST-004 | Public user cannot access admin endpoint | Protect admin API. | HTTP 403. | Critical |
| ST-005 | Expired token rejected | Prevent stale access. | HTTP 401. | High |
| ST-006 | Failed login creates audit event | Prove auth auditability. | Audit event exists. | High |
| ST-007 | Public response redacts sensitive fields | Prevent leakage. | Sensitive fields absent. | Critical |
| ST-008 | Rate limit returns safe error | Prevent abuse. | HTTP 429, no secrets. | High |

## 9. Acceptance Criteria

Phase 10 is complete only when:

- Unit tests are defined and runnable.
- Integration tests cover full acta lifecycle.
- Modified document detection is proven.
- Duplicate acta handling is proven.
- PREP mismatch detection is proven.
- Audit immutability is proven.
- Blockchain verification is proven with mock provider.
- Public endpoint redaction is proven.
- Security role boundaries are proven.
- Observability endpoints are tested.
- Test execution instructions are documented.

## 10. CI Pipeline

Added workflow:

```text
.github/workflows/test.yml
```

Pipeline stages:

- Dependency install
- Syntax check
- Unit tests
- Integration tests
- Security tests
- Observability tests
- E2E smoke tests
- Full backend validation with coverage
- Artifact upload

## 11. Coverage Targets

Recommended targets:

- Unit coverage: 80% minimum for services
- Critical services: 90% target
- Security and audit logic: no untested critical paths
- Endpoint authorization matrix: 100% of protected endpoint groups tested

Critical modules:

- `HashService`
- `DocumentIntegrityService`
- `AuditService`
- `TraceabilityService`
- `BlockchainService`
- `AuthService`
- `PermissionService`
- `AlertService`

## 12. Failure Simulation

Tests and plan simulate:

- Storage object modified
- Storage object missing
- Blockchain provider unavailable
- Invalid token
- Unauthorized role
- Duplicate acta
- PREP mismatch
- Audit write failure
- Metrics endpoint checks
- Public API abuse

Database unavailable should be validated in Docker or staging through readiness endpoint failure injection.

## 13. Test Reporting

CI generates:

- `test-results.xml`
- `coverage.xml`
- `htmlcov/`
- `test-reports/*.xml`

Templates added:

- `actatrace-backend/test-reports/security-test-summary.md`
- `actatrace-backend/test-reports/release-readiness-report.md`

## 14. Release Readiness Checklist

- [ ] Tests passing
- [ ] Coverage threshold met
- [ ] Migrations tested
- [ ] RBAC matrix tested
- [ ] Audit immutability tested
- [ ] Public redaction tested
- [ ] Hash mismatch tested
- [ ] Blockchain mock verified
- [ ] Observability tested
- [ ] Environment variables reviewed
- [ ] Secrets absent from repo
- [ ] Docker Compose starts successfully
- [ ] Health endpoint passes
- [ ] README updated
- [ ] Known limitations documented

## 15. Anti-Overengineering Guardrails

Phase 10 does not add:

- AI fraud detection tests
- Electronic voting tests
- Real public blockchain dependency in CI
- Kubernetes-based test infrastructure
- Heavy load testing platform
- Complex chaos engineering platform
- Real personal voter data
- Browser automation beyond frontend scope

## 16. Run Commands

Unit tests:

```bash
cd actatrace-backend
pytest tests/unit
```

Integration tests:

```bash
pytest tests/integration
```

Security tests:

```bash
pytest tests/security
```

Observability tests:

```bash
pytest tests/observability
```

E2E smoke tests:

```bash
pytest tests/e2e
```

Full validation:

```bash
pytest app/tests tests --cov=app --cov-report=xml --cov-report=html --junitxml=test-results.xml
```

Docker test profile:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## 17. Known Limitations

- Load testing is planned but not implemented in Phase 10.
- Browser automation for the citizen portal is excluded from backend validation.
- Database unavailable simulation is better executed in Docker/staging than in the in-memory test suite.
- Real Hyperledger Fabric is not used in CI; mock provider validates behavior.
- Coverage thresholds are recommended but not enforced yet as hard CI gates.

## 18. Phase 11 Recommendation

Recommended next phase:

**Phase 11 — Documentation, Demo Scenario, and MVP Packaging**

Phase 11 should build:

- Final README
- Architecture documentation
- API documentation
- Security documentation
- Audit documentation
- Demo dataset
- Demo flow
- Public presentation script
- MVP acceptance checklist
- Deployment notes
