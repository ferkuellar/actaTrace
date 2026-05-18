terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = local.tags
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  tags = merge(var.tags, {
    Project            = "ActaTrace"
    Environment        = var.environment
    Owner              = var.owner
    ManagedBy          = "Terraform"
    CostCenter         = var.cost_center
    DataClassification = var.data_classification
    Criticality        = var.criticality
    Purpose            = "electoral-traceability"
  })
}

module "networking" {
  source              = "../../modules/networking"
  name_prefix         = local.name_prefix
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  allowed_cidr_blocks = var.allowed_cidr_blocks
  tags                = local.tags
}

module "secrets" {
  source      = "../../modules/secrets"
  name_prefix = local.name_prefix
  secret_names = [
    "database-url",
    "jwt-secret-key",
    "s3-access-key",
    "s3-secret-key",
    "grafana-admin-password"
  ]
  tags = local.tags
}

module "object_storage" {
  source              = "../../modules/object_storage"
  bucket_name         = var.storage_bucket_name
  enable_versioning   = var.enable_storage_versioning
  deletion_protection = false
  tags                = local.tags
}

module "postgres" {
  source                  = "../../modules/postgres"
  name_prefix             = local.name_prefix
  subnet_ids              = module.networking.private_subnet_ids
  vpc_security_group_ids  = [module.networking.database_security_group_id]
  database_name           = var.database_name
  database_username       = var.database_username
  database_password       = var.database_password
  database_instance_class = var.database_instance_class
  backup_retention_days   = var.backup_retention_days
  deletion_protection     = false
  skip_final_snapshot     = true
  tags                    = local.tags
}

module "iam" {
  source             = "../../modules/iam"
  name_prefix        = local.name_prefix
  bucket_arn         = module.object_storage.bucket_arn
  secret_arns        = module.secrets.secret_arns
  log_group_arn      = module.monitoring.backend_log_group_arn
  github_repo        = var.github_repo
  enable_github_oidc = var.enable_github_oidc
  tags               = local.tags
}

module "monitoring" {
  source      = "../../modules/monitoring"
  name_prefix = local.name_prefix
  enabled     = var.enable_monitoring
  tags        = local.tags
}

module "backend_service" {
  source             = "../../modules/backend_service"
  name_prefix        = local.name_prefix
  cluster_name       = "${local.name_prefix}-cluster"
  subnet_ids         = module.networking.private_subnet_ids
  security_group_ids = [module.networking.backend_security_group_id]
  assign_public_ip   = false
  backend_image      = var.backend_image
  backend_cpu        = var.backend_cpu
  backend_memory     = var.backend_memory
  desired_count      = var.backend_desired_count
  execution_role_arn = module.iam.ecs_execution_role_arn
  task_role_arn      = module.iam.backend_task_role_arn
  log_group_name     = module.monitoring.backend_log_group_name
  container_port     = 8000
  environment_variables = {
    ENVIRONMENT         = var.environment
    SERVICE_NAME        = "actatrace-api"
    STORAGE_PROVIDER    = "s3"
    S3_BUCKET_NAME      = module.object_storage.bucket_name
    BLOCKCHAIN_PROVIDER = var.enable_blockchain_node ? "hyperledger_fabric" : "mock"
  }
  secret_arns = module.secrets.secret_arns
  tags        = local.tags
}

module "blockchain_optional" {
  source                = "../../modules/blockchain_optional"
  enabled               = var.enable_blockchain_node
  name_prefix           = local.name_prefix
  fabric_channel_name   = var.fabric_channel_name
  fabric_chaincode_name = var.fabric_chaincode_name
  tags                  = local.tags
}

