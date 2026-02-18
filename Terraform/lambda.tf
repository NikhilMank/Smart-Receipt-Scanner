resource "aws_lambda_function" "receipt-api" {
  function_name = "receipt-api"
  handler = "lambda_function.lambda_handler"
  runtime = "python3.12"
  role = aws_iam_role.receipt-api-role.arn
  timeout = 3
  filename = "./../api/api_lambda.zip"
  source_code_hash = filebase64sha256("./../api/api_lambda.zip")
}