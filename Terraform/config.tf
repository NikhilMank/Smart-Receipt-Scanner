variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "receipt-scanner"
}

variable "image_tag" {  # tag of the image to be deployed as lambda function
  type = string
  default = "latest"
}