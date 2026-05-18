variable "name_prefix" { type = string }
variable "cluster_name" { type = string }
variable "subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "assign_public_ip" { type = bool }
variable "backend_image" { type = string }
variable "backend_cpu" { type = number }
variable "backend_memory" { type = number }
variable "desired_count" { type = number }
variable "execution_role_arn" { type = string }
variable "task_role_arn" { type = string }
variable "log_group_name" { type = string }
variable "container_port" { type = number }
variable "environment_variables" { type = map(string) }
variable "secret_arns" { type = map(string) }
variable "tags" { type = map(string) }

