resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-db-subnets"
  subnet_ids = var.subnet_ids
  tags       = merge(var.tags, { Name = "${var.name_prefix}-db-subnets" })
}

resource "aws_db_instance" "this" {
  identifier                 = "${var.name_prefix}-postgres"
  engine                     = "postgres"
  engine_version             = "16"
  instance_class             = var.database_instance_class
  allocated_storage          = 20
  max_allocated_storage      = 100
  db_name                    = var.database_name
  username                   = var.database_username
  password                   = var.database_password
  db_subnet_group_name       = aws_db_subnet_group.this.name
  vpc_security_group_ids     = var.vpc_security_group_ids
  publicly_accessible        = false
  storage_encrypted          = true
  backup_retention_period    = var.backup_retention_days
  deletion_protection        = var.deletion_protection
  skip_final_snapshot        = var.skip_final_snapshot
  auto_minor_version_upgrade = true
  copy_tags_to_snapshot      = true
  apply_immediately          = false
  tags                       = merge(var.tags, { Name = "${var.name_prefix}-postgres", Purpose = "system-of-record" })
}

