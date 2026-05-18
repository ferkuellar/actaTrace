resource "aws_secretsmanager_secret" "this" {
  for_each = toset(var.secret_names)
  name     = "${var.name_prefix}/${each.key}"
  tags     = merge(var.tags, { Name = "${var.name_prefix}/${each.key}", Purpose = "runtime-secret" })
}

