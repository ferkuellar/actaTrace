# Infrastructure Security

Security controls:

- Least privilege IAM roles
- Runtime role separated from deployment role
- Private RDS
- Private S3 bucket
- S3 public access block enabled
- Encryption at rest for RDS and S3
- Secrets stored in Secrets Manager
- Remote Terraform state encrypted
- Production deletion protection recommended
- No static cloud credentials in repository

Production requirements:

- Use GitHub OIDC or equivalent workload identity.
- Restrict Terraform state access.
- Require plan review before apply.
- Enable backup restore tests.
- Audit IAM permissions before launch.

