# Infrastructure Architecture

ActaTrace uses a simple AWS reference architecture:

- VPC with public and private subnets
- ECS Fargate backend service in private subnets
- RDS PostgreSQL as system of record
- S3 private bucket for electoral documents
- Secrets Manager for runtime configuration
- CloudWatch logs for container output
- Prometheus/Grafana handled through Phase 8 local stack or a managed equivalent

PostgreSQL remains the system of record. S3 stores files. Blockchain stores only hashes and critical event proofs when enabled.

## Network Boundaries

- Public ingress is limited to API/load balancer paths.
- Database is private.
- Object storage is private.
- Monitoring administration is restricted.
- SSH is disabled by default.

