# ActaTrace Infrastructure

Terraform infrastructure for ActaTrace, organized by environment and reusable modules.

Default provider target: AWS.

This structure provisions the foundation for:

- FastAPI backend on ECS Fargate
- PostgreSQL on RDS
- Private S3 document bucket
- IAM runtime roles
- Secrets Manager references
- CloudWatch logs
- Optional monitoring integration
- Optional blockchain placeholder disabled by default

## Environments

```text
infra/environments/dev
infra/environments/staging
infra/environments/prod
```

Each environment has:

- `main.tf`
- `variables.tf`
- `outputs.tf`
- `terraform.tfvars.example`
- `backend.tf.example`

Copy examples before use:

```bash
cp backend.tf.example backend.tf
cp terraform.tfvars.example terraform.tfvars
```

Do not commit `terraform.tfvars`, `backend.tf`, or `.terraform/`.

## Commands

```bash
terraform fmt -recursive
cd infra/environments/dev
terraform init
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Security Notes

- Do not place secrets in committed files.
- Use remote encrypted state with locking for staging and prod.
- Keep databases private.
- Keep document buckets private.
- Use OIDC for CI/CD where supported.
- Review every production plan before apply.

