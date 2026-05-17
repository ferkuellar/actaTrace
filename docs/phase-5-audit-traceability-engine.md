# Phase 5 — Audit and Traceability Engine

## 1. Phase Objective

Phase 5 implements the audit and traceability engine for ActaTrace. The objective is to let authorized users reconstruct, verify, and explain the complete lifecycle of an acta using PostgreSQL as the system of record, external document storage for files, SHA-256 hashes for integrity, and blockchain anchors only as proof records.

This phase supports:

- Immutable audit logs.
- Full acta traceability timelines.
- Custody timelines.
- Document integrity events.
- PREP validation events.
- Blockchain anchor events.
- Inconsistency detection.
- Alert generation.
- Forensic reconstruction.

This phase does not implement electronic voting, AI fraud detection, or blockchain-as-database behavior.

## 2. Core Principle

Every relevant event must answer:

- Who performed the action?
- What changed?
- When did it happen?
- Where did it happen?
- Which entity was affected?
- What was the previous state?
- What is the new state?
- Was the change authorized?
- Is there evidence supporting it?
- Is the event linked to a document hash or blockchain anchor?

## 3. Audit Model

`AuditLog` is the append-only record of operational, security, verification, and forensic events.

Fields added or enforced in Phase 5:

- `request_id`
- `correlation_id`
- `actor_user_id`
- `actor_role`
- `actor_organization`
- `action`
- `entity_type`
- `entity_id`
- `event_category`
- `event_severity`
- `before_state`
- `after_state`
- `changed_fields`
- `ip_address`
- `user_agent`
- `geo_location`
- `evidence_document_id`
- `related_acta_id`
- `related_polling_station_id`
- `blockchain_anchor_id`
- `hash_value`
- `metadata_json`
- `created_at`

Event categories:

- `AUTH`
- `ACTA`
- `DOCUMENT`
- `CUSTODY`
- `PREP`
- `BLOCKCHAIN`
- `SECURITY`
- `SYSTEM`
- `VERIFICATION`

Event severities:

- `INFO`
- `WARNING`
- `CRITICAL`

## 4. Immutable Log Rules

Application-level immutability is enforced with SQLAlchemy lifecycle listeners:

- `before_update` rejects audit log mutation.
- `before_delete` rejects audit log deletion.
- No API endpoint exposes audit update or delete operations.
- Business services emit audit events through `AuditService`.

Recommended database-level hardening for production:

- Add PostgreSQL triggers rejecting `UPDATE` and `DELETE` on `audit_logs`.
- Restrict database roles so the application can only insert and select audit logs.
- Ship audit logs to external append-only storage for long-term preservation.
- Monitor failed mutation attempts as `SECURITY` events.

## 5. Event Model

### 5.1 AuditEvent

The persisted forensic record. Implemented by `AuditLog`.

### 5.2 TraceabilityEvent

The timeline projection returned by `TraceabilityService`. It is assembled from:

- `AuditLog`
- `CustodyEvent`
- `PREPResult`
- `BlockchainAnchor`
- `Alert`

### 5.3 AlertEvent

An operational risk or inconsistency detected by `InconsistencyDetectionService` and persisted as `Alert`.

Each event includes:

- who
- what
- when
- where
- before state
- after state
- evidence
- severity
- verification status

## 6. Traceability Engine

`TraceabilityService` reconstructs an acta lifecycle by aggregating events from the system of record.

Included event sources:

- Acta creation and updates.
- Document upload, hashing, retrieval, verification, and mismatch events.
- Custody transfer, reception, validation, rejection, escalation, and closure events.
- PREP capture and validation events.
- Blockchain anchoring events.
- Approval and rejection events.
- Integrity mismatch events.
- Alert events.

Output is ordered chronologically.

## 7. Traceability API

Endpoints under `/api/v1/traceability`:

- `GET /traceability/actas/{acta_id}/timeline`
- `GET /traceability/actas/{acta_id}/forensic-report`
- `GET /traceability/polling-stations/{polling_station_id}`
- `GET /traceability/audit-events`
- `GET /traceability/public/actas/{acta_code}`

Internal endpoints require `SUPERVISOR`, `AUDITOR`, or `OBSERVADOR` depending on sensitivity. Forensic reports and audit event search are restricted to `SUPERVISOR` and `AUDITOR`, with `ADMIN_ELECTORAL` allowed by the global RBAC rule.

## 8. Alert Model

`Alert` captures detected inconsistencies or operational risks.

Fields:

- `id`
- `alert_type`
- `severity`
- `status`
- `entity_type`
- `entity_id`
- `acta_id`
- `polling_station_id`
- `detected_by`
- `description`
- `evidence`
- `recommendation`
- `assigned_to`
- `resolved_by`
- `resolution_notes`
- `resolved_at`
- `created_at`
- `updated_at`

Alert types:

- `PREP_ACTA_MISMATCH`
- `DUPLICATE_ACTA`
- `DUPLICATE_DOCUMENT_HASH`
- `DOCUMENT_HASH_MISMATCH`
- `BLOCKCHAIN_HASH_MISMATCH`
- `CUSTODY_GAP`
- `UNAUTHORIZED_STATE_TRANSITION`
- `STORAGE_OBJECT_MISSING`
- `SUSPICIOUS_ACCESS`
- `MANUAL_REVIEW_REQUIRED`

Alert statuses:

- `OPEN`
- `IN_REVIEW`
- `RESOLVED`
- `FALSE_POSITIVE`
- `ESCALATED`

## 9. Alert API

Endpoints under `/api/v1/alerts`:

- `GET /alerts`
- `GET /alerts/{alert_id}`
- `PATCH /alerts/{alert_id}/assign`
- `PATCH /alerts/{alert_id}/resolve`
- `PATCH /alerts/{alert_id}/escalate`

Rules:

- Only `SUPERVISOR`, `AUDITOR`, or `ADMIN_ELECTORAL` can manage alerts.
- Alert assignment, resolution, and escalation create audit logs.
- Public users cannot access internal alerts.
- Resolution requires notes.

## 10. Inconsistency Detection

`InconsistencyDetectionService` detects:

### 10.1 PREP vs Acta Mismatch

If `PREPResult.total_votes` differs from `Acta.expected_total_votes`, a `PREP_ACTA_MISMATCH` critical alert is created. If acta structured totals are unavailable, a `MANUAL_REVIEW_REQUIRED` warning is created.

### 10.2 Duplicate Acta

If the same acta code appears more than once, a `DUPLICATE_ACTA` critical alert is created. The database unique constraint remains the first line of defense.

### 10.3 Duplicate Document Hash

If the same SHA-256 hash appears in more than one document record, a `DUPLICATE_DOCUMENT_HASH` warning is created. The database unique constraint prevents normal duplicates; detection remains useful for imported or repaired data.

### 10.4 Document Hash Mismatch

If a document is marked `MISMATCH` or `CORRUPTED`, a `DOCUMENT_HASH_MISMATCH` critical alert is created.

### 10.5 Storage Object Missing

If a document is marked `STORAGE_MISSING`, a `STORAGE_OBJECT_MISSING` critical alert is created.

### 10.6 Custody Gap

If a `TRANSFERRED` custody event is not followed by `RECEIVED`, `VALIDATED`, or `REJECTED` within `CUSTODY_RECEPTION_THRESHOLD_HOURS`, a `CUSTODY_GAP` warning is created.

## 11. Before/After State Capture

Implemented helpers:

- `capture_state(entity) -> dict`
- `diff_states(before, after) -> dict`

Sensitive fields are masked:

- passwords
- password hashes
- tokens
- JWTs
- secrets
- raw storage paths
- storage keys
- storage URLs

## 12. Public-Safe Redaction

Public timeline responses remove:

- internal user IDs
- email addresses
- IP addresses
- raw user agents
- raw storage paths
- private notes
- internal metadata
- security-sensitive details

Public responses expose only:

- `acta_code`
- `polling_station_code`
- event type
- timestamp
- verification status
- hash proof
- public document status
- blockchain anchor proof when present

## 13. Database Schema Updates

Migration:

- `e2d84e333650_add_audit_traceability_alerts.py`

Tables updated:

- `audit_logs`
- `alerts`

Indexes added:

- `audit_logs.entity_type`
- `audit_logs.entity_id`
- `audit_logs.related_acta_id`
- `audit_logs.actor_user_id`
- `audit_logs.created_at`
- `audit_logs.event_category`
- `audit_logs.event_severity`
- `audit_logs.request_id`
- `audit_logs.correlation_id`
- `alerts.alert_type`
- `alerts.status`
- `alerts.severity`
- `alerts.acta_id`
- `alerts.polling_station_id`
- `alerts.created_at`

## 14. Environment Variables

Added:

```env
CUSTODY_RECEPTION_THRESHOLD_HOURS=4
ENABLE_ALERT_GENERATION=true
ENABLE_PUBLIC_TRACEABILITY=true
AUDIT_LOG_RETENTION_DAYS=2555
PUBLIC_TRACEABILITY_RATE_LIMIT_PER_MINUTE=60
```

## 15. Security Requirements

Implemented:

- RBAC on traceability and alert endpoints.
- Append-only audit enforcement at application level.
- Public redaction for public timeline endpoint.
- Pagination for audit search.
- No audit update/delete endpoint.
- Sensitive field masking in state capture.
- Alert actions recorded in audit logs.

Recommended:

- Add rate limiting to public traceability endpoints.
- Add database triggers for audit immutability.
- Ship audit events to external archival storage.
- Monitor failed audit mutation attempts.

## 16. Tests

Phase 5 adds tests for:

- AuditLog update rejection.
- AuditLog delete rejection.
- Chronological acta timeline.
- Forensic report core sections.
- PREP mismatch alert generation.
- Document hash mismatch critical alert.
- Custody gap warning alert.
- Public timeline redaction.
- Alert assignment audit event.
- Alert resolution validation.

Current result:

```text
36 passed
```

## 17. Known Limitations

- Database-level immutability triggers are documented but not yet added as SQL triggers.
- Duplicate detection is mostly defensive because current unique constraints prevent standard duplicate records.
- Public endpoint rate limiting is documented and configured, but no rate limiter middleware is installed yet.
- Forensic reports are generated live from source tables; snapshot caching is intentionally deferred.
- Unauthorized lifecycle transition detection is not yet fully integrated into every state-changing service.

## 18. Anti-Overengineering Guardrails

Phase 5 intentionally does not add:

- AI fraud detection.
- Predictive anomaly models.
- Kafka.
- Event sourcing.
- Blockchain as audit database.
- Electronic voting.
- Public user accounts.
- Complex notification system.
- Kubernetes.
- Data warehouse.

## 19. Phase 6 Recommendation

Recommended next phase:

**Phase 6 — Citizen Verification Portal**

Phase 6 should build:

- Public search by acta code and polling station.
- Public-safe acta verification page.
- Hash verification result.
- Blockchain proof display.
- Traceability timeline.
- Institutional visual design.
- Plain-language trust indicators with no crypto jargon.

Phase 6 must not build:

- Electronic voting.
- Vote casting.
- Public user accounts unless explicitly approved.
- Crypto wallet login.
- Complex analytics.
- AI fraud detection.
