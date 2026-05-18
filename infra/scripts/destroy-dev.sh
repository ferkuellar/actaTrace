#!/usr/bin/env sh
set -eu

cd infra/environments/dev
terraform init
terraform destroy -var-file=terraform.tfvars

