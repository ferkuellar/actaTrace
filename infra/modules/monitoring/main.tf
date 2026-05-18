resource "aws_cloudwatch_log_group" "backend" {
  name              = "/actatrace/${var.name_prefix}/backend"
  retention_in_days = 30
  tags              = merge(var.tags, { Name = "${var.name_prefix}-backend-logs", Purpose = "application-logs" })
}

resource "aws_cloudwatch_dashboard" "operations" {
  count          = var.enabled ? 1 : 0
  dashboard_name = "${var.name_prefix}-operations"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 3
        properties = {
          markdown = "# ActaTrace ${var.name_prefix} Operations\nUse Prometheus/Grafana for application metrics. CloudWatch retains container logs."
        }
      }
    ]
  })
}

