terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "6.32.1"
    }
    null = {
      source = "hashicorp/null"
      version = "3.2.4"
    }
  }
}

provider "aws" {
  # Configuration options
  region = var.aws_region
}