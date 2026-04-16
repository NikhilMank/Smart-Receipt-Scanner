# IAM Role for api-receipt lambda function

resource "aws_iam_role" "receipt-api-role" {
  name = "receipt-api-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach AWS Managed Policies

resource "aws_iam_role_policy_attachment" "cognitoPowerUser" {
  role       = aws_iam_role.receipt-api-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonCognitoPowerUser"
}

resource "aws_iam_role_policy_attachment" "DynamoDBFullAccess" {
  role       = aws_iam_role.receipt-api-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "LambdaBasicExecution" {
  role       = aws_iam_role.receipt-api-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Custom Policy 1
resource "aws_iam_policy" "CognitoAndUsersTableAccess" {
  name        = "CognitoAndUsersTableAccess"
  description = "Custom policy 1 for Lambda"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cognito-idp:AdminCreateUser",
                "cognito-idp:AdminInitiateAuth"
            ],
            "Resource": aws_cognito_user_pool.receipt_scanner.arn
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem"
            ],
            "Resource": "*"
        }
    ]
})
}

resource "aws_iam_role_policy_attachment" "CognitoAndUsersTableAccess_attach" {
  role       = aws_iam_role.receipt-api-role.name
  policy_arn = aws_iam_policy.CognitoAndUsersTableAccess.arn
}

# Custom Policy 2 
resource "aws_iam_policy" "S3AccessPolicy" {
  name        = "S3AccessPolicy"
  description = "Allow the API Lambda to sign and access receipt uploads in the app bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.public_storage.arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "S3AccessPolicy_attach" {
  role       = aws_iam_role.receipt-api-role.name
  policy_arn = aws_iam_policy.S3AccessPolicy.arn
}

# Lambda trust policy
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "receipt_scanner_lambda_role" {
  name               = "ReceiptProcessor-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# 1) CloudWatchLogsFullAccess
resource "aws_iam_role_policy_attachment" "lambda_cw_logs_full" {
  role       = aws_iam_role.receipt_scanner_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# 2) AmazonS3ReadOnlyAccess
resource "aws_iam_role_policy_attachment" "lambda_s3_readonly" {
  role       = aws_iam_role.receipt_scanner_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

# 3) AmazonDynamoDBFullAccess
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_full" {
  role       = aws_iam_role.receipt_scanner_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

# 4) Custom role policy (your JSON as an inline policy)
resource "aws_iam_role_policy" "lambda_custom_logs_policy" {
  name = "receipt-processor-custom-logs"
  role = aws_iam_role.receipt_scanner_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "logs:CreateLogGroup"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}