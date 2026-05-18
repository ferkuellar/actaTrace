#!/usr/bin/env sh
set -eu

ENVIRONMENT="${1:-dev}"

cd "infra/environments/${ENVIRONMENT}"
terraform init
terraform apply "${ENVIRONMENT}.tfplan"

