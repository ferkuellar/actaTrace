resource "aws_cloudwatch_log_group" "fabric_placeholder" {
  count             = var.enabled ? 1 : 0
  name              = "/actatrace/${var.name_prefix}/fabric-placeholder"
  retention_in_days = 30
  tags              = merge(var.tags, { Purpose = "optional-blockchain-placeholder" })
}

resource "null_resource" "disabled_notice" {
  count = var.enabled ? 0 : 1

  triggers = {
    message = "Blockchain infrastructure is disabled by default. Use mock provider in dev and provision Fabric only through an approved enterprise design."
  }
}

