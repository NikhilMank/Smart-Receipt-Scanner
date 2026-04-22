# create a repository in ECR
resource "aws_ecr_repository" "receipt_scanner" {
  name = "receipt-ocr-lambda"
  force_delete = true
  image_tag_mutability = "MUTABLE"
}
resource "aws_ecr_lifecycle_policy" "receipt_scanner" {
  repository = aws_ecr_repository.receipt_scanner.name
    policy = <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep only 2 latest images",
        "selection": {
            "tagStatus": "any",
            "countType": "imageCountMoreThan",
            "countNumber": 6
        },
        "action": {
            "type": "expire"
        }
    }
  ]
}
EOF
}

locals {
  image_uri = "${aws_ecr_repository.receipt_scanner.repository_url}:${var.image_tag}"
}

resource "null_resource" "docker_build_and_push" {
  triggers = {
    dockerfile_hash = filesha256("${path.module}/../lambda/Dockerfile")
    context_hash = filesha256("${path.module}/../lambda/app.py")
    requirements = filesha256("${path.module}/../lambda/requirements.txt")
    image_tag = var.image_tag
    repo_url = aws_ecr_repository.receipt_scanner.repository_url
  }

  # provisioner "local-exec" {
  #   interpreter = [ "/usr/bin/env", "bash", "-lc" ]
  #   command = <<EOT
  #   set -e
  #   aws ecr get-login-password --region ${var.aws_region} \
  #       | docker login --username AWS --password-stdin ${aws_ecr_repository.receipt_scanner.repository_url}
  #   docker build -t ${local.image_uri} ${path.module}/../lambda
  #   docker tag ${var.image_tag} ${aws_ecr_repository.receipt_scanner.repository_url}:${var.image_tag}
  #   docker push ${local.image_uri}
  #   EOT
  # }

  provisioner "local-exec" {
    interpreter = [ "/usr/bin/env", "bash", "-lc" ]
    command = "${path.module}/scripts/build_and_push.sh ${var.aws_region} ${aws_ecr_repository.receipt_scanner.repository_url} ${local.image_uri} ${path.module}/../lambda"
  }

  depends_on = [ aws_ecr_repository.receipt_scanner ]
}

output "ecr_repository_url" {
  value = aws_ecr_repository.receipt_scanner.repository_url
}