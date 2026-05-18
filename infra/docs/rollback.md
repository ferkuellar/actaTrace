# Rollback

Terraform is not an application rollback tool. Treat infrastructure rollback carefully.

## Application Rollback

1. Identify the previous backend image tag.
2. Update `backend_image`.
3. Run `terraform plan`.
4. Apply only the service image change.
5. Run `/health/ready`.

## Database Migrations

Database rollback must be planned separately. Do not rely on Terraform to reverse schema changes.

## Infrastructure Rollback

1. Preserve current Terraform state.
2. Review the previous known-good commit.
3. Run `terraform plan`.
4. Confirm no destructive change affects production data.
5. Apply only after approval.

Never destroy production databases or document buckets as part of routine rollback.
