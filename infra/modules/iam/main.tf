data "aws_iam_policy_document" "ecs_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${var.name_prefix}-ecs-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
  tags               = merge(var.tags, { Purpose = "ecs-execution" })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "backend_task" {
  name               = "${var.name_prefix}-backend-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
  tags               = merge(var.tags, { Purpose = "backend-runtime" })
}

data "aws_iam_policy_document" "backend_runtime" {
  statement {
    sid       = "ReadRuntimeSecrets"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = values(var.secret_arns)
  }

  statement {
    sid = "DocumentBucketAccess"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ]
    resources = [
      var.bucket_arn,
      "${var.bucket_arn}/*"
    ]
  }

  statement {
    sid = "WriteLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["${var.log_group_arn}:*"]
  }
}

resource "aws_iam_policy" "backend_runtime" {
  name   = "${var.name_prefix}-backend-runtime"
  policy = data.aws_iam_policy_document.backend_runtime.json
  tags   = var.tags
}

resource "aws_iam_role_policy_attachment" "backend_runtime" {
  role       = aws_iam_role.backend_task.name
  policy_arn = aws_iam_policy.backend_runtime.arn
}

data "aws_iam_policy_document" "github_oidc_assume" {
  count = var.enable_github_oidc ? 1 : 0

  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:*"]
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "github_deploy" {
  count              = var.enable_github_oidc ? 1 : 0
  name               = "${var.name_prefix}-github-deploy"
  assume_role_policy = data.aws_iam_policy_document.github_oidc_assume[0].json
  tags               = merge(var.tags, { Purpose = "github-actions-deploy" })
}

