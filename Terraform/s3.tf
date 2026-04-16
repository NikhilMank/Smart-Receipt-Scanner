# Create S3 bucket for receipt scanner frontend
resource "aws_s3_bucket" "frontend" {
  bucket = "receipt-scanner-frontend"
  force_destroy = true #allows bucket to be deleted even if it contains objects by Terraform destroy
}
# configure the bucket to serve as a static website
resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  index_document {
    suffix = "index.html" # the default page to serve when a user visits the root URL of the website
  }
  error_document {
    key = "error.html" # the page to serve when a user encounters an error (e.g., 404 Not Found)
  }
}
# Allow public read access to the bucket (for website hosting)
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls = false
  block_public_policy = false
  ignore_public_acls = false
  restrict_public_buckets = false
}
# Allow public read access to all objects in the bucket
resource "aws_s3_bucket_policy" "frontend_public_read" {
  bucket = aws_s3_bucket.frontend.id
  policy = data.aws_iam_policy_document.frontend_public_read.json
  depends_on = [ aws_s3_bucket_public_access_block.frontend ]
}
data "aws_iam_policy_document" "frontend_public_read" {
  statement {
    sid = "PublicReadGetObject"
    effect = "Allow"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions = [
      "s3:GetObject"
    ]
    resources = [
      "${aws_s3_bucket.frontend.arn}/*"
    ]
  }
}
    


# Create S3 bucket for receipt scanner public storage
resource "aws_s3_bucket" "public_storage" {
  bucket = "receipt-scanner-publicstorage"
}
resource "aws_s3_bucket_public_access_block" "public_storage" {
  bucket = aws_s3_bucket.public_storage.id

  block_public_acls = false
  block_public_policy = false
  ignore_public_acls = false
  restrict_public_buckets = false
}
resource "aws_s3_bucket_policy" "public_storage" {
  bucket = aws_s3_bucket.public_storage.id
  policy = data.aws_iam_policy_document.public_storage_policy.json

  depends_on = [ 
    aws_s3_bucket_public_access_block.public_storage
   ]
}
data "aws_iam_policy_document" "public_storage_policy" {

  # 1️⃣ Allow public presigned uploads
  statement {
    sid    = "AllowPresignedUploads"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.public_storage.arn}/*"
    ]
  }

  # 2️⃣ Allow Lambda (from another AWS account) access
  statement {
    sid    = "AllowLambdaAccess"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::190164554245:root"]
    }

    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.public_storage.arn}/*"
    ]
  }
}
# Create S3 bucket for receipts scanner dev
resource "aws_s3_bucket" "nikhil_dev" {
  bucket = "receipt-scanner-nikhil-dev"
}

locals {
  repo_root = abspath("${path.module}")
}

resource "null_resource" "build_and_upload_frontend" {

  provisioner "local-exec" {
    interpreter = ["/usr/bin/env", "bash", "-lc"]
    command = "${local.repo_root}/scripts/deploy_frontend.sh '${local.repo_root}' '${aws_s3_bucket.frontend.bucket}' '${aws_api_gateway_stage.prod.invoke_url}'"
  }

  depends_on = [
    aws_api_gateway_stage.prod,
    aws_s3_bucket.frontend,
    aws_s3_bucket.public_storage
  ]
}

# Cross origin resource sharing configuration
resource "aws_s3_bucket_cors_configuration" "public_storage_cors" {
  bucket = aws_s3_bucket.public_storage.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "GET", "HEAD", "POST", "DELETE"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

output "Website_url" {
  value = aws_s3_bucket_website_configuration.frontend.website_endpoint
}