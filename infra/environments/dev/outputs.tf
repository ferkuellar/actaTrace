output "backend_cluster_name" {
  value = module.backend_service.cluster_name
}

output "backend_service_name" {
  value = module.backend_service.service_name
}

output "database_endpoint" {
  value     = module.postgres.endpoint
  sensitive = true
}

output "document_bucket_name" {
  value = module.object_storage.bucket_name
}

output "secrets" {
  value     = module.secrets.secret_arns
  sensitive = true
}

