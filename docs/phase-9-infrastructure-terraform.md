# Phase 9 — Infrastructure and Deployment with Terraform

## 1. Phase Objective

Phase 9 designs reproducible infrastructure for ActaTrace using Terraform.

The infrastructure supports:

- Backend API service
- PostgreSQL database
- S3-compatible document storage
- Optional blockchain/Fabric node infrastructure
- Monitoring stack
- Secure networking
- Environment separation
- CI/CD deployment pipeline
- Secrets management
- Audit-ready infrastructure documentation

This phase does not introduce Kubernetes, electronic voting, or complex blockchain production infrastructure.

## 2. Infrastructure Principles

ActaTrace infrastructure follows these principles:

- Infrastructure as Code first
- Reproducible environments
- Least privilege IAM
- Explicit network boundaries
- Secrets outside code
- Environment separation
- Observable by default
- Tagged resources
- Cost-aware design
- Simple deployment model before complex orchestration
- No manual cloud configuration without documentation

## 3. Target Environments

### 3.1 Dev

Purpose:

- Developer testing
- Feature validation
- Low-cost infrastructure
- Mock blockchain provider allowed

Characteristics:

- Smaller resources
- Relaxed availability
- Minimal cost
- Manual approval optional

### 3.2 Staging

Purpose:

- Pre-production validation
- Integration testing
- Security testing
- Demo readiness

Characteristics:

- Production-like configuration
- Separate database
- Real object storage
- Monitoring enabled
- Optional Fabric test network

### 3.3 Prod

Purpose:

- Production deployment

Characteristics:

- Strong security
- Backups enabled
- Encryption enabled
- Monitoring and alerts enabled
- Strict IAM
- Protected secrets
- Restricted public access
- Change control required

## 4. Cloud-Agnostic Structure

Created structure:

```text
infra/
├── README.md
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── modules/
│   ├── networking/
│   ├── backend_service/
│   ├── postgres/
│   ├── object_storage/
│   ├── monitoring/
│   ├── iam/
│   ├── secrets/
│   └── blockchain_optional/
├── scripts/
│   ├── validate.sh
│   ├── plan.sh
│   ├── apply.sh
│   └── destroy-dev.sh
└── docs/
    ├── architecture.md
    ├── deployment.md
    ├── security.md
    └── rollback.md
```

Each environment includes:

- `main.tf`
- `variables.tf`
- `outputs.tf`
- `terraform.tfvars.example`
- `backend.tf.example`

## 5. Infrastructure Components

### 5.1 Networking

The networking module includes:

- AWS VPC
- Public subnet placeholders
- Private subnets for backend and database placement
- Backend security group
- Database security group
- Controlled API ingress
- Private database ingress only from backend security group
- Egress rules

TLS termination should be added at a load balancer or managed API ingress layer before production launch.

### 5.2 Backend Service

The backend service module deploys FastAPI using ECS Fargate.

Requirements supported:

- Docker-based deployment
- Health checks against `/health`
- Environment variables
- Secret injection from Secrets Manager
- CloudWatch logs
- Private subnet placement
- Configurable CPU, memory, image, and desired count

The current module is intentionally minimal and does not include ALB creation yet. Add ALB/TLS in the production ingress hardening step.

### 5.3 PostgreSQL

The PostgreSQL module provisions RDS PostgreSQL.

Requirements supported:

- Private subnet group
- No public access
- Encryption at rest
- Automated backups
- Configurable retention
- Separate database per environment
- Production deletion protection parameter

### 5.4 Object Storage

The object storage module provisions a private S3 bucket.

Requirements supported:

- Public access blocked
- Server-side encryption
- Versioning
- Multipart upload cleanup
- Backend-only access through IAM

Public write is never allowed.

### 5.5 Secrets Management

The secrets module creates Secrets Manager secret placeholders.

Secrets:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `BLOCKCHAIN_PROVIDER`
- Fabric credentials when enabled
- Grafana admin password if provisioned

Rules:

- Do not commit `terraform.tfvars` with secrets.
- Prefer secret values populated outside Terraform where possible.
- Use secret references in runtime services.
- Avoid storing sensitive secret values directly in Terraform state.

### 5.6 Monitoring

The monitoring module provisions:

- CloudWatch log group for backend logs
- Minimal CloudWatch dashboard placeholder

Phase 8 already provides Prometheus/Grafana files for local operation. In AWS, Prometheus/Grafana can later be deployed as managed services, ECS services, or replaced by CloudWatch dashboards depending on operational preference.

### 5.7 Optional Blockchain Infrastructure

The blockchain module is disabled by default:

```hcl
enable_blockchain_node = false
```

Supported strategy:

- Dev uses mock provider.
- Staging may use Fabric test network if required.
- Production Fabric network remains a future enterprise deployment.

Phase 9 does not force production Fabric deployment.

## 6. Cloud Provider Option

Default implementation: **AWS-style Terraform**.

AWS was selected because it maps cleanly to:

- ECS Fargate for containerized backend
- RDS PostgreSQL
- S3 for private document storage
- IAM for least privilege runtime roles
- Secrets Manager
- CloudWatch logs
- Optional Prometheus/Grafana deployment

The module boundaries can later be adapted to Azure or OCI:

- ECS Fargate maps to Azure Container Apps or OCI Container Instances.
- RDS maps to Azure Database for PostgreSQL or OCI PostgreSQL.
- S3 maps to Azure Blob Storage or OCI Object Storage.
- IAM maps to Entra ID managed identities or OCI IAM.

## 7. AWS Reference Implementation

Implemented modules:

- VPC and subnets
- Security groups
- ECS Fargate backend service
- RDS PostgreSQL
- S3 bucket
- IAM runtime roles
- Secrets Manager secret placeholders
- CloudWatch logs
- Optional blockchain placeholder

Not added:

- EKS
- Service mesh
- Multi-region active-active
- Transit gateway
- Advanced WAF

These are future hardening options, not Phase 9 requirements.

## 8. Terraform Variables

Common variables:

- `project_name`
- `environment`
- `region`
- `owner`
- `cost_center`
- `allowed_cidr_blocks`
- `backend_image`
- `backend_cpu`
- `backend_memory`
- `backend_desired_count`
- `database_instance_class`
- `database_name`
- `database_username`
- `database_password`
- `backup_retention_days`
- `storage_bucket_name`
- `enable_monitoring`
- `enable_blockchain_node`
- `enable_public_api`
- `tags`

## 9. Tagging Strategy

Every resource must include:

- `Project = ActaTrace`
- `Environment = dev/staging/prod`
- `Owner`
- `ManagedBy = Terraform`
- `CostCenter`
- `DataClassification`
- `Criticality`
- `Purpose`

Rule:

If a resource has no owner, it should not exist.

## 10. IAM and Least Privilege

IAM roles are separated:

- ECS execution role
- Backend task runtime role
- Optional GitHub OIDC deploy role

Runtime role permissions:

- Read only required Secrets Manager secrets
- Access only the configured document bucket
- Write only to configured CloudWatch log group

Rules:

- No wildcard admin policies in prod
- No permanent access keys where avoidable
- Use GitHub OIDC for CI/CD
- Separate deployment role from runtime role

## 11. Network Security

Network controls:

- Public ingress only to API/load balancer when added
- Database private only
- Object storage private only
- Monitoring admin UI restricted
- Grafana protected
- Prometheus not public
- SSH disabled by default
- Admin access through secure mechanism only

## 12. Deployment Pipeline

Created workflows:

```text
.github/workflows/
├── terraform-validate.yml
├── terraform-plan-dev.yml
├── terraform-apply-dev.yml
├── terraform-plan-staging.yml
├── terraform-apply-staging.yml
├── terraform-plan-prod.yml
└── backend-deploy.yml
```

Rules:

- Pull requests run `terraform fmt`, `terraform validate`, and plan.
- Staging apply is manual.
- Production only has plan workflow in Phase 9.
- Use OIDC where supported.
- Store no cloud credentials in repository.
- Upload plans as artifacts.
- Use GitHub environment protection rules.

## 13. Backend Deployment Pipeline

`backend-deploy.yml`:

1. Runs backend tests.
2. Builds Docker image.
3. Pushes image to ECR.
4. Forces ECS service deployment.
5. Runs health check against `/health/ready`.

Image scanning is recommended as the next security enhancement.

## 14. Terraform State Management

State strategy:

- Remote backend required for staging/prod.
- State locking required.
- Separate state per environment.
- State encryption required.
- Access restricted.
- Local state files must never be committed.

Only `backend.tf.example` is committed.

`.gitignore` excludes:

- `.terraform/`
- `terraform.tfstate`
- `terraform.tfvars`
- `*.tfplan`
- `backend.tf`

## 15. Security Requirements

Infrastructure supports:

- Encryption at rest
- Encryption in transit recommendation
- Private database access
- Private object storage
- Restricted IAM
- Secret manager
- Audit logs
- Backup policy
- Access logs where practical
- Production deletion protection recommendation

## 16. Backup and Recovery

PostgreSQL:

- Automated backups configured through `backup_retention_days`.
- Point-in-time recovery recommended for staging/prod.
- Restore tests required before production.

Object storage:

- S3 versioning recommended and enabled by variable.
- Lifecycle cleanup for incomplete multipart uploads.
- Production bucket deletion should be restricted.

Recovery:

- Test restore procedures.
- Restrict backup access.
- Preserve audit and document records during incident response.

## 17. Observability Integration

Infrastructure supports:

- Backend health endpoint
- Metrics endpoint
- CloudWatch container logs
- Prometheus/Grafana local stack from Phase 8
- Future managed Prometheus/Grafana deployment
- Alerting rules from `actatrace-backend/monitoring/alert-rules.yml`

## 18. Cost Control

Cost controls:

- Smaller dev resources
- Optional blockchain node disabled by default
- No expensive HA in dev
- Configurable CPU and memory
- Configurable database instance class
- S3 lifecycle cleanup
- Full tagging
- `destroy-dev.sh` only for dev

## 19. Terraform Module Interfaces

### networking

Inputs:

- `name_prefix`
- `vpc_cidr`
- `availability_zones`
- `allowed_cidr_blocks`
- `tags`

Outputs:

- `vpc_id`
- `public_subnet_ids`
- `private_subnet_ids`
- `backend_security_group_id`
- `database_security_group_id`

Resources:

- VPC
- Subnets
- Internet gateway
- Security groups

Security notes:

- Database allows ingress only from backend security group.

### backend_service

Inputs:

- Image, CPU, memory, desired count
- Subnets and security groups
- IAM execution/task roles
- Log group
- Environment variables
- Secret ARNs

Outputs:

- ECS cluster name
- ECS service name
- Task definition ARN

Resources:

- ECS cluster
- Task definition
- ECS service

Security notes:

- Secrets are injected through ECS secrets.
- Backend runs in private subnets by default.

### postgres

Inputs:

- Subnets
- Security groups
- Database name
- Username/password
- Instance class
- Backup retention
- Deletion protection

Outputs:

- Endpoint
- Address
- Database name

Resources:

- DB subnet group
- RDS PostgreSQL instance

Security notes:

- Public access disabled.
- Storage encryption enabled.

### object_storage

Inputs:

- Bucket name
- Versioning flag
- Deletion protection flag
- Tags

Outputs:

- Bucket name
- Bucket ARN

Resources:

- S3 bucket
- Public access block
- Encryption
- Versioning
- Lifecycle configuration

Security notes:

- Bucket is private by default.

### iam

Inputs:

- Bucket ARN
- Secret ARNs
- Log group ARN
- GitHub repo
- OIDC flag

Outputs:

- ECS execution role ARN
- Backend task role ARN
- GitHub deploy role ARN

Resources:

- IAM roles
- IAM policies
- Optional GitHub OIDC role

Security notes:

- Runtime role only reads required secrets and document bucket.

### secrets

Inputs:

- Secret names
- Tags

Outputs:

- Secret ARNs

Resources:

- Secrets Manager secret placeholders

Security notes:

- Secret values should be populated outside Terraform when possible.

### monitoring

Inputs:

- Name prefix
- Enabled flag
- Tags

Outputs:

- Backend log group name
- Backend log group ARN

Resources:

- CloudWatch log group
- Minimal CloudWatch dashboard

### blockchain_optional

Inputs:

- Enabled flag
- Fabric channel name
- Fabric chaincode name

Outputs:

- Enabled status
- Fabric metadata

Resources:

- Placeholder log group when enabled
- Disabled notice when not enabled

Security notes:

- Disabled by default to avoid premature Fabric infrastructure.

## 20. Example Terraform Code

Provider:

```hcl
provider "aws" {
  region = var.region

  default_tags {
    tags = local.tags
  }
}
```

Networking:

```hcl
module "networking" {
  source              = "../../modules/networking"
  name_prefix         = local.name_prefix
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  allowed_cidr_blocks = var.allowed_cidr_blocks
  tags                = local.tags
}
```

PostgreSQL:

```hcl
module "postgres" {
  source                 = "../../modules/postgres"
  name_prefix            = local.name_prefix
  subnet_ids             = module.networking.private_subnet_ids
  vpc_security_group_ids = [module.networking.database_security_group_id]
  database_name          = var.database_name
  database_username      = var.database_username
  database_password      = var.database_password
  database_instance_class = var.database_instance_class
  backup_retention_days  = var.backup_retention_days
  deletion_protection    = true
  skip_final_snapshot    = false
  tags                   = local.tags
}
```

Object storage:

```hcl
module "object_storage" {
  source            = "../../modules/object_storage"
  bucket_name       = var.storage_bucket_name
  enable_versioning = true
  tags              = local.tags
}
```

Backend service:

```hcl
module "backend_service" {
  source             = "../../modules/backend_service"
  backend_image      = var.backend_image
  backend_cpu        = var.backend_cpu
  backend_memory     = var.backend_memory
  desired_count      = var.backend_desired_count
  subnet_ids         = module.networking.private_subnet_ids
  security_group_ids = [module.networking.backend_security_group_id]
}
```

## 21. Validation Commands

General:

```bash
terraform fmt -recursive
terraform init
terraform validate
terraform plan
terraform apply
```

Dev:

```bash
cd infra/environments/dev
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

Staging:

```bash
cd infra/environments/staging
terraform init
terraform plan -var-file=terraform.tfvars
```

Prod:

```bash
cd infra/environments/prod
terraform init
terraform plan -var-file=terraform.tfvars
```

## 22. Release and Rollback

Deployment checklist:

- Tests passed.
- Docker image built and tagged.
- Terraform plan reviewed.
- Secrets present in Secrets Manager.
- Database migrations reviewed separately.
- Health endpoint available.
- Monitoring active.

Rollback strategy:

- Roll back application by deploying previous image tag.
- Treat database rollback separately.
- Do not use Terraform destroy as rollback.
- Backup Terraform state before major changes.
- Review plan for destructive changes before apply.

Terraform rollback limitations:

- Terraform reconciles desired infrastructure state.
- It does not automatically reverse data migrations.
- It can destroy resources if configuration is removed.
- Production changes require manual review.

## 23. Infrastructure Audit Checklist

- [ ] No secrets committed
- [ ] Remote state configured
- [ ] State locking enabled
- [ ] Resources tagged
- [ ] IAM least privilege reviewed
- [ ] Database private
- [ ] Storage private
- [ ] Encryption enabled
- [ ] Backups enabled
- [ ] Monitoring enabled
- [ ] Health checks configured
- [ ] Public ingress reviewed
- [ ] Prod deletion protection enabled
- [ ] Terraform plan reviewed before apply

## 24. Anti-Overengineering Guardrails

Phase 9 does not add:

- Kubernetes
- Service mesh
- Multi-cloud active-active
- Multi-region DR
- Kafka
- Data warehouse
- Complex blockchain production network
- Manual server snowflakes
- Unmanaged public database
- Public object storage
- Broad admin IAM policies

## 25. Phase 10 Recommendation

Recommended next phase:

**Phase 10 — Validation, Testing, and Release Readiness**

Phase 10 should build:

- Unit test coverage
- Integration test coverage
- API test suite
- Security tests
- Audit validation tests
- Blockchain verification tests
- Document integrity tests
- Load and smoke tests
- Release checklist
- Final MVP acceptance criteria
