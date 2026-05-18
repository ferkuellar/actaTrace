# Phase 8 — Observability and Monitoring

## 1. Phase Objective

Phase 8 adds operational visibility to ActaTrace so it can be run as a public-sector critical system, not as a demo.

The platform must provide visibility into:

- System health
- API performance
- Acta processing
- Document integrity verification
- Hash mismatches
- PREP inconsistencies
- Blockchain anchoring failures
- Audit event generation
- Security events
- Storage failures
- Public portal usage
- Operational incidents

ActaTrace does not implement electronic voting. Observability must never expose sensitive data in logs, metrics, dashboards, or alert payloads.

## 2. Core Observability Principle

ActaTrace must answer these operational questions:

- Is the system healthy?
- Are actas being processed?
- Are hashes matching?
- Are documents available?
- Are blockchain anchors working?
- Are inconsistencies increasing?
- Are public verification endpoints stable?
- Are security events occurring?
- Can we reconstruct an incident?

Observability is part of auditability. Metrics and logs support operations, while PostgreSQL audit records remain the forensic source of truth.

## 3. Observability Stack

The Phase 8 stack is intentionally practical:

- **Prometheus** for metrics scraping and alert evaluation.
- **Grafana** for operational dashboards.
- **Structured JSON logs** for request, security, audit, and business events.
- **OpenTelemetry-ready structure** without adding a tracing backend yet.
- **FastAPI middleware** for request metrics.
- **PostgreSQL readiness checks** for operational health.
- **MinIO/S3 metrics compatibility** through provider-level checks and future exporter support.
- **Alertmanager optional** for production notification routing.

Kubernetes, service mesh, SIEM, and distributed tracing backends are excluded from Phase 8.

## 4. Metrics Design

Metrics are exposed at:

```text
GET /metrics
GET /api/v1/metrics
```

The root `/metrics` endpoint is intended for Prometheus. In production it should be protected through network controls, gateway authentication, or private service networking.

### 4.1 API Metrics

Implemented:

- `http_requests_total`
- `http_request_duration_seconds`
- `http_requests_in_progress`
- `http_errors_total`
- `http_rate_limited_total`

Labels:

- `method`
- `route`
- `status_code`
- `role`
- `public_endpoint`

### 4.2 Acta Metrics

Defined for service-level instrumentation:

- `actas_created_total`
- `actas_processed_total`
- `actas_verified_total`
- `actas_rejected_total`
- `actas_by_status`
- `acta_processing_duration_seconds`

Labels:

- `status`
- `municipality`
- `district`
- `election_type`

### 4.3 Document Integrity Metrics

Defined and partially linked through audit events:

- `documents_uploaded_total`
- `documents_verified_total`
- `document_hash_mismatches_total`
- `document_storage_missing_total`
- `document_integrity_checks_total`
- `document_upload_size_bytes`

Labels:

- `integrity_status`
- `storage_provider`
- `file_type`

### 4.4 PREP Validation Metrics

Defined:

- `prep_results_captured_total`
- `prep_results_validated_total`
- `prep_mismatches_total`
- `prep_requires_review_total`

Labels:

- `validation_status`
- `municipality`
- `district`

### 4.5 Blockchain Metrics

Defined:

- `blockchain_anchor_attempts_total`
- `blockchain_anchor_success_total`
- `blockchain_anchor_failures_total`
- `blockchain_verification_attempts_total`
- `blockchain_verification_failures_total`
- `blockchain_anchor_duration_seconds`

Labels:

- `provider`
- `network`
- `anchor_type`
- `verification_status`

### 4.6 Audit Metrics

Implemented:

- `audit_events_total`
- `audit_log_write_failures_total`
- `audit_tamper_attempts_total`

Labels:

- `event_category`
- `event_severity`
- `action`

### 4.7 Security Metrics

Implemented:

- `auth_login_success_total`
- `auth_login_failed_total`
- `auth_forbidden_total`
- `auth_unauthorized_total`
- `public_rate_limit_exceeded_total`
- `suspicious_access_detected_total`

Labels:

- `role`
- `endpoint_group`
- `reason`

### 4.8 Alert Metrics

Defined:

- `alerts_created_total`
- `alerts_open_total`
- `alerts_resolved_total`
- `alerts_escalated_total`

Labels:

- `alert_type`
- `severity`
- `status`

## 5. Structured Logging

Logs use JSON when `LOG_FORMAT=json`.

Every log entry should include, when available:

- `timestamp`
- `level`
- `service`
- `environment`
- `request_id`
- `correlation_id`
- `user_id`
- `role`
- `method`
- `path`
- `status_code`
- `latency_ms`
- `action`
- `entity_type`
- `entity_id`
- `result`
- `error_code`

Never log:

- Passwords
- JWT tokens
- Secrets
- Private keys
- Raw document contents
- Full sensitive metadata

Sensitive keys such as `password`, `token`, `access_token`, `refresh_token`, `secret`, and `private_key` are masked by the JSON formatter.

## 6. Log Categories

Recommended logger categories:

- `api.request`
- `api.response`
- `auth.event`
- `acta.event`
- `document.event`
- `custody.event`
- `prep.event`
- `blockchain.event`
- `audit.event`
- `security.event`
- `storage.event`
- `alert.event`
- `system.health`

## 7. Health Checks

Implemented endpoints:

```text
GET /health
GET /health/live
GET /health/ready
GET /api/v1/health
GET /api/v1/health/live
GET /api/v1/health/ready
```

### GET /health

Returns basic service status:

```json
{
  "status": "ok",
  "service": "actatrace-api",
  "version": "0.1.0",
  "environment": "local",
  "timestamp": "2026-05-17T00:00:00Z"
}
```

### GET /health/live

Returns a simple liveness response.

### GET /health/ready

Checks:

- Database connectivity
- Audit log table readability
- Storage provider configuration
- Blockchain provider configuration

Readiness failures return HTTP `503`.

### GET /metrics

Returns Prometheus format metrics. Do not expose this endpoint directly to the public internet.

## 8. Grafana Dashboards

Dashboard JSON files are stored under:

```text
actatrace-backend/monitoring/grafana/dashboards/
```

### 8.1 Executive Operational Dashboard

Shows:

- Total actas processed
- Verified actas
- Open critical alerts
- Hash mismatch count
- PREP mismatch count
- System request rate

### 8.2 Technical API Dashboard

Shows:

- API request rate
- Latency p95
- Error rate
- Top failing routes
- Rate limit events

### 8.3 Document Integrity Dashboard

Shows:

- Documents uploaded
- Documents verified
- Hash mismatches
- Storage missing events
- Integrity check breakdown

### 8.4 Blockchain Verification Dashboard

Shows:

- Anchor attempts
- Anchor failures
- Anchor duration p95
- Provider/network breakdown

### 8.5 Security and Audit Dashboard

Shows:

- Failed logins
- Forbidden attempts
- Audit events by severity
- Tamper attempts
- Security-relevant trends

### 8.6 Public Portal Dashboard

Public portal metrics are represented through public endpoint labels in API metrics. A dedicated dashboard should be added once Phase 6 public endpoints stabilize.

## 9. Alerting Rules

Prometheus alert rules are stored in:

```text
actatrace-backend/monitoring/alert-rules.yml
```

### 9.1 Critical Alerts

| Name | Condition | Severity | Business impact | Suggested response | Runbook |
| --- | --- | --- | --- | --- | --- |
| `AuditLogWriteFailure` | `increase(audit_log_write_failures_total[5m]) > 0` | Critical | Forensic reconstruction may be incomplete. | Stop affected workflows and inspect database health. | `docs/runbooks/audit-log-write-failure.md` |
| `DocumentHashMismatchDetected` | `increase(document_hash_mismatches_total[5m]) >= 1` | Critical | Evidence may have been altered or incorrectly stored. | Start hash mismatch incident workflow. | `docs/runbooks/hash-mismatch.md` |
| `AuditTamperAttempt` | `increase(audit_tamper_attempts_total[5m]) > 0` | Critical | Audit evidence may be under attack. | Lock down admin access and preserve logs. | `docs/runbooks/audit-tamper-attempt.md` |
| `DatabaseUnavailable` | Backend target unavailable | Critical | API and public verification may be unavailable. | Check backend, database, and network health. | `docs/runbooks/backend-unavailable.md` |
| `PrepMismatchSpike` | `increase(prep_mismatches_total[10m]) >= 1` | Critical | PREP may not match registered acta evidence. | Assign auditor review. | `docs/runbooks/prep-mismatch.md` |

### 9.2 Warning Alerts

| Name | Condition | Severity | Business impact | Suggested response | Runbook |
| --- | --- | --- | --- | --- | --- |
| `ApiLatencyElevated` | p95 latency above threshold | Warning | Verification workflows may feel slow. | Review backend, database, and storage latency. | `docs/runbooks/api-latency.md` |
| `ApiErrorRateElevated` | 5xx error rate above threshold | Warning | API reliability is degraded. | Inspect failing routes and recent changes. | `docs/runbooks/api-errors.md` |
| `BlockchainAnchoringDelay` | Anchor failures in recent window | Warning | Proof anchoring may be delayed. | Check provider health and retry idempotently. | `docs/runbooks/blockchain-anchor-failure.md` |
| `PublicVerificationFailuresIncreasing` | Public endpoint failures increasing | Warning | Citizen verification may be degraded. | Review public endpoint health and rate limits. | `docs/runbooks/public-verification-failures.md` |

### 9.3 Informational Alerts

Informational alerts should be added after production baselines exist:

- Large batch of actas processed
- High public verification traffic
- New alert category detected

## 10. Incident Response Support

### 10.1 Hash Mismatch Incident

1. Identify `document_id` and `acta_id`.
2. Retrieve the acta forensic report.
3. Compare database hash, current file hash, and blockchain hash.
4. Review storage access events.
5. Escalate the alert.
6. Preserve document, audit, and storage evidence.
7. Document the incident outcome.

### 10.2 PREP Mismatch Incident

1. Identify `acta_id` and `prep_result_id`.
2. Compare PREP record with registered acta data.
3. Review custody timeline.
4. Review actor history.
5. Assign auditor or supervisor.
6. Resolve or escalate.

### 10.3 Blockchain Anchor Failure

1. Check provider health.
2. Review failed transaction metadata.
3. Confirm PostgreSQL state remains correct.
4. Retry only when the operation is idempotent.
5. Audit the retry action.

### 10.4 Unauthorized Access Spike

1. Identify endpoint group.
2. Review IP and user patterns.
3. Check rate limits.
4. Disable compromised users if needed.
5. Preserve logs and audit events.

## 11. Implementation Architecture

Added modules:

```text
app/
├── observability/
│   ├── __init__.py
│   ├── metrics.py
│   ├── logging_config.py
│   ├── health.py
│   ├── middleware.py
│   └── instrumentation.py
├── api/
│   └── v1/
│       ├── health.py
│       └── metrics.py
└── monitoring/
    ├── prometheus.yml
    ├── alert-rules.yml
    └── grafana/
        ├── dashboards/
        └── provisioning/
```

## 12. FastAPI Metrics Implementation

`PrometheusMetricsMiddleware` captures:

- Request count
- Latency
- Status code
- Route path
- HTTP method
- Exceptions through 500 labels

Metrics are generated with `prometheus_client`.

## 13. Docker Compose Updates

Docker Compose includes:

- `backend` on port `8000`
- `postgres` on port `5432`
- `minio` on ports `9000` and `9001`
- `prometheus` on port `9090`
- `grafana` on port `3001`

Run locally:

```bash
cd actatrace-backend
docker compose up --build
```

Open:

```text
Backend:    http://localhost:8000
Metrics:    http://localhost:8000/metrics
Prometheus: http://localhost:9090
Grafana:    http://localhost:3001
```

## 14. Environment Variables

Added:

```env
SERVICE_NAME=actatrace-api
SERVICE_VERSION=0.1.0
ENVIRONMENT=local
LOG_FORMAT=json
LOG_LEVEL=INFO
ENABLE_METRICS=true
METRICS_PATH=/metrics
ENABLE_HEALTH_READY=true
PROMETHEUS_SCRAPE_INTERVAL=15s
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=change-me
ALERT_HASH_MISMATCH_THRESHOLD=1
ALERT_PREP_MISMATCH_THRESHOLD=1
ALERT_API_ERROR_RATE_THRESHOLD=0.05
ALERT_API_LATENCY_P95_SECONDS=1.5
```

Production must replace default Grafana credentials.

## 15. Audit and Observability Linkage

Major audit actions are mapped to metrics:

| Audit event | Metric |
| --- | --- |
| `DOCUMENT_HASH_MISMATCH` | `document_hash_mismatches_total` |
| `PREP_ACTA_MISMATCH` | `prep_mismatches_total` |
| `AUDIT_LOG_TAMPER_ATTEMPT` | `audit_tamper_attempts_total` |
| `BLOCKCHAIN_ANCHOR_FAILED` | `blockchain_anchor_failures_total` |
| `AUTH_LOGIN_FAILED` | `auth_login_failed_total` |
| `PUBLIC_RATE_LIMIT_EXCEEDED` | `public_rate_limit_exceeded_total` |

## 16. Data Privacy in Observability

Rules:

- Use IDs or aggregate dimensions, not personal details, in metrics labels.
- Avoid high-cardinality labels such as raw `user_id`.
- Do not log raw document content.
- Do not log full sensitive metadata.
- Do not expose raw hashes in high-volume logs unless needed for forensic review.
- Mask passwords, tokens, secrets, and private keys.
- Keep public search terms out of logs where possible.

## 17. Tests

Implemented tests cover:

- `/health/ready` database readiness
- `/metrics` Prometheus output
- API request metrics
- HTTP error metrics
- Hash mismatch metric from audit event
- Failed login metric
- Structured log masking

Run:

```bash
cd actatrace-backend
pytest app/tests/test_observability.py
```

## 18. Known Limitations

- Dashboards are starter dashboards, not final production SLO dashboards.
- Alertmanager routing is documented but not deployed in Phase 8.
- OpenTelemetry tracing is not enabled yet.
- PostgreSQL exporter and MinIO exporter are not included yet.
- Metrics labels are conservative to avoid sensitive data and high cardinality.

## 19. Production Recommendations

- Protect `/metrics` through private networking or gateway authentication.
- Add Alertmanager for email, chat, or incident-management routing.
- Add PostgreSQL and MinIO exporters for deeper dependency visibility.
- Define SLOs for public verification, document integrity checks, and anchoring.
- Store Grafana credentials in a secret manager.
- Review logs for sensitive leakage before production.
- Add runbooks under `docs/runbooks/`.

## 20. Anti-Overengineering Guardrails

Phase 8 does not add:

- Kubernetes
- Service mesh
- Distributed tracing backend
- SIEM integration
- Data warehouse
- Machine learning anomaly detection
- Complex log aggregation platform
- Multi-region monitoring
- Electronic voting monitoring

## 21. Phase 9 Recommendation

Recommended next phase:

**Phase 9 — Infrastructure and Deployment with Terraform**

Phase 9 should build:

- Reproducible infrastructure
- Environment separation
- Backend deployment target
- PostgreSQL deployment
- Object storage configuration
- Monitoring deployment
- Secrets management
- Network security
- Terraform modules
- Deployment documentation

Phase 9 must not introduce electronic voting, blockchain-as-database behavior, or public exposure of sensitive operational endpoints.
