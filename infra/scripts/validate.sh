#!/usr/bin/env sh
set -eu

terraform fmt -recursive -check

for env in dev staging prod; do
  (
    cd "infra/environments/${env}"
    terraform init -backend=false
    terraform validate
  )
done

