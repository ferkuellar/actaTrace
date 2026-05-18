resource "aws_ecs_cluster" "this" {
  name = var.cluster_name
  tags = merge(var.tags, { Purpose = "backend-runtime" })
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.name_prefix}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.backend_cpu
  memory                   = var.backend_memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "actatrace-backend"
      image     = var.backend_image
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          protocol      = "tcp"
        }
      ]
      environment = [
        for key, value in var.environment_variables : {
          name  = key
          value = value
        }
      ]
      secrets = [
        for key, arn in var.secret_arns : {
          name      = upper(replace(key, "-", "_"))
          valueFrom = arn
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = var.log_group_name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "backend"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:${var.container_port}/health').read()\""]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 30
      }
    }
  ])

  tags = var.tags
}

data "aws_region" "current" {}

resource "aws_ecs_service" "backend" {
  name            = "${var.name_prefix}-backend"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = var.security_group_ids
    assign_public_ip = var.assign_public_ip
  }

  tags = merge(var.tags, { Purpose = "backend-api" })
}

