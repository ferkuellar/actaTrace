variable "name_prefix" { type = string }
variable "vpc_cidr" { type = string }
variable "availability_zones" { type = list(string) }
variable "allowed_cidr_blocks" { type = list(string) }
variable "tags" { type = map(string) }

