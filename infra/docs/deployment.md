# Deployment

## Dev

```bash
cd infra/environments/dev
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Staging

Staging requires remote state, state locking, and manual approval.

```bash
cd infra/environments/staging
terraform init
terraform plan -var-file=terraform.tfvars
```

## Prod

Production apply must be manual and reviewed.

```bash
cd infra/environments/prod
terraform init
terraform plan -var-file=terraform.tfvars
```

Apply only after security, audit, and operations review.

