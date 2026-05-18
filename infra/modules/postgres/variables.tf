variable "name_prefix" { type = string }
variable "subnet_ids" { type = list(string) }
variable "vpc_security_group_ids" { type = list(string) }
variable "database_name" { type = string }
variable "database_username" { type = string }
variable "database_password" {
  type      = string
  sensitive = true
}
variable "database_instance_class" { type = string }
variable "backup_retention_days" { type = number }
variable "deletion_protection" { type = bool }
variable "skip_final_snapshot" { type = bool }
variable "tags" { type = map(string) }
