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
            "Resource": "arn:aws:cognito-idp:eu-central-1:*:userpool/eu-central-1_Eg9Fy4q8u"
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

# Custom Policy 2 .-- not necessary
# resource "aws_iam_policy" "S3AccessPolicy" {
#   name        = "S3AccessPolicy"
#   description = "Custom policy 2 for Lambda"

#   policy = jsonencode({
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": [
#                 "s3:PutObject",
#                 "s3:PutObjectAcl",
#                 "s3:GetObject"
#             ],
#             "Resource": "*"
#         }
#     ]
# })
# }

# resource "aws_iam_role_policy_attachment" "S3AccessPolicy_attach" {
#   role       = aws_iam_role.receipt-api-role.name
#   policy_arn = aws_iam_policy.S3AccessPolicy.arn
# }