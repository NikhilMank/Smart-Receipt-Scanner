resource "aws_lambda_function" "receipt-api" {
  function_name = "receipt-api"
  handler = "api_lambda.lambda_handler"
  runtime = "python3.12"
  role = aws_iam_role.receipt-api-role.arn
  timeout = 3
  filename = "./../api/api_lambda.zip"
  source_code_hash = filebase64sha256("./../api/api_lambda.zip")

  environment {
    variables = {
      COGNITO_CLIENT_ID = aws_cognito_user_pool_client.receipt_scanner.id
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.receipt_scanner.id
      DYNAMODB_RECEIPTS_TABLE = aws_dynamodb_table.receipts.name
      DYNAMODB_USERS_TABLE = aws_dynamodb_table.users.name
      S3_BUCKET_NAME = aws_s3_bucket.public_storage.bucket
    }
  }
}
resource "aws_lambda_permission" "apigw_all_routes" {
  statement_id = "AllowAPIGatewayInvoleAll"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.receipt-api.function_name
  principal = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.receipt_scanner.execution_arn}/*/*/*"
}

resource "aws_lambda_function" "receipt-ocr-container" {
  function_name = "receipt-ocr-container"
  package_type = "Image"
  image_uri = local.image_uri

  timeout = 300 # set to 5 minutes to allow for processing time
  memory_size = 1024
  role = aws_iam_role.receipt_scanner_lambda_role.arn

  environment {
    variables = {
      DYNAMODB_RECEIPTS_TABLE = aws_dynamodb_table.receipts.name
      S3_BUCKET_NAME = aws_s3_bucket.public_storage.bucket
    }
  }

  depends_on = [ null_resource.docker_build_and_push ]  # Ensure the image is built and pushed before creating the Lambda function
}