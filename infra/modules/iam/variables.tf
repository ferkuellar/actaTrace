variable "name_prefix" { type = string }
variable "bucket_arn" { type = string }
variable "secret_arns" { type = map(string) }
variable "log_group_arn" { type = string }
variable "github_repo" { type = string }
variable "enable_github_oidc" { type = bool }
variable "tags" { type = map(string) }

