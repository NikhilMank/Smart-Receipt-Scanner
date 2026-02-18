# Create S3 bucket for receipt scanner frontend
resource "aws_s3_bucket" "frontend" {
  bucket = "receipt-scanner-frontend"
}

# Create S3 bucket for receipt scanner public storage
resource "aws_s3_bucket" "public_storage" {
  bucket = "receipt-scanner-publicstorage"
}

# Create S3 bucket for receipts scanner dev
resource "aws_s3_bucket" "nikhil_dev" {
  bucket = "receipt-scanner-nikhil-dev"
}