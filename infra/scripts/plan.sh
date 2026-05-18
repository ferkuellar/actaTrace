#!/usr/bin/env sh
set -eu

ENVIRONMENT="${1:-dev}"

cd "infra/environments/${ENVIRONMENT}"
terraform init
terraform plan -var-file=terraform.tfvars -out="${ENVIRONMENT}.tfplan"

