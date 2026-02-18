resource "aws_api_gateway_rest_api" "receipt_scanner" { # API Gateway REST API
  name        = "receipt-scanner-api"
  description = "Receipt Scanner REST API"

  endpoint_configuration {
    types = ["EDGE"]
  }
}

resource "aws_api_gateway_authorizer" "cognito" { # Cognito Authorizer for protected endpoints
  name = "cognito-authorizer"
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  type = "COGNITO_USER_POOLS"
  provider_arns = [aws_cognito_user_pool.receipt_scanner.arn]
  identity_source = "method.request.header.Authorization"
  authorizer_result_ttl_in_seconds = 300 # Cache authorizer results for 5 minutes to improve performance
}
#######################################################################################

resource "aws_api_gateway_resource" "analytics" { #/analytics
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id   = aws_api_gateway_rest_api.receipt_scanner.root_resource_id
  path_part = "analytics"
}

resource "aws_api_gateway_resource" "metrics" { # /analytics/metrics
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_resource.analytics.id
  path_part = "metrics"
}
resource "aws_api_gateway_method" "metrics_get" { # /analytics/metrics-GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.metrics.id
  http_method = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "metrics_get_lambda" { # Lambda Integration for GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.metrics.id
  http_method = aws_api_gateway_method.metrics_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.receipt-api.invoke_arn
}
resource "aws_api_gateway_method" "metrics_options" { # /analytics/metrics-OPTIONS(For CORS)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.metrics.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "metrics_options" { # Mock Integration for OPTIONS
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.metrics.id
  http_method = aws_api_gateway_method.metrics_options.http_method

  type = "MOCK"

  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_method_response" "metrics_options" {  # Method Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.metrics.id
  http_method = aws_api_gateway_method.metrics_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}
resource "aws_api_gateway_integration_response" "metrics_options" { # Integration Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.metrics.id
  http_method = aws_api_gateway_method.metrics_options.http_method
  status_code = aws_api_gateway_method_response.metrics_options.status_code

  response_parameters = {
      "method.response.header.Access-Control-Allow-Origin" = "'*'"
      "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
      "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    }

    response_templates = {
      "application/json" = ""
    }
}


resource "aws_api_gateway_resource" "patterns" { # /analytics/patterns
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_resource.analytics.id
  path_part = "patterns"
}
resource "aws_api_gateway_method" "patterns_get" { # /analytics/patterns-GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.patterns.id
  http_method = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "patterns_get_lambda" { # Lambda Integration for patterns-GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.patterns.id
  http_method = aws_api_gateway_method.patterns_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.receipt-api.invoke_arn
}
resource "aws_api_gateway_method" "patterns_options" { # /analytics/patterns-OPTIONS(For CORS)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.patterns.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "patterns_options" { # Mock Integration for OPTIONS
 rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
 resource_id = aws_api_gateway_resource.patterns.id
 http_method = aws_api_gateway_method.patterns_options.http_method
  
  type = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_method_response" "patterns_options" {  # Method Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.patterns.id
  http_method = aws_api_gateway_method.patterns_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}
resource "aws_api_gateway_integration_response" "patterns_options" { # Integration Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.patterns.id
  http_method = aws_api_gateway_method.patterns_options.http_method
  status_code = aws_api_gateway_method_response.patterns_options.status_code

  response_parameters = {
      "method.response.header.Access-Control-Allow-Origin" = "'*'"
      "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
      "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    }  
}

resource "aws_api_gateway_resource" "monthly" { # /analytics/monthly
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_resource.analytics.id
  path_part = "monthly"
}
resource "aws_api_gateway_method" "monthly_get" { # /analytics/monthly-GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.monthly.id
  http_method = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  request_parameters = {
    "method.request.header.Authorization" = true
  }
}
resource "aws_api_gateway_integration" "monthly_get_lambda" { # Lambda Integration for monthly-GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.monthly.id
  http_method = aws_api_gateway_method.monthly_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.receipt-api.invoke_arn
}
resource "aws_api_gateway_method" "monthly_options" { # /analytics/monthly-OPTIONS(For CORS)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.monthly.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method_response" "monthly_options" {  # Method Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.monthly.id
  http_method = aws_api_gateway_method.monthly_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}
resource "aws_api_gateway_integration_response" "monthly_options" { # Integration Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.monthly.id
  http_method = aws_api_gateway_method.monthly_options.http_method
  status_code = aws_api_gateway_method_response.monthly_options.status_code

  response_parameters = {
      "method.response.header.Access-Control-Allow-Origin" = "'*'"
      "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
      "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    }
}


resource "aws_api_gateway_resource" "summary" { # /analytics/summary
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_resource.analytics.id
  path_part = "summary"
}
resource "aws_api_gateway_method" "summary_get" { # /analytics/summary-GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.summary.id
  http_method = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  request_parameters = {
    "method.request.header.Authorization" = true
  }
}
resource "aws_api_gateway_integration" "summary_get_lambda" { # Lambda Integration for summary-GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.summary.id
  http_method = aws_api_gateway_method.summary_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.receipt-api.invoke_arn
}
resource "aws_api_gateway_method" "summary_options" { # /analytics/summary-OPTIONS(For CORS)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.summary.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method_response" "summary_options" { # Method Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.summary.id
  http_method = aws_api_gateway_method.summary_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}
resource "aws_api_gateway_integration_response" "summary_options" { # Integration Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.summary.id
  http_method = aws_api_gateway_method.summary_options.http_method
  status_code = aws_api_gateway_method_response.summary_options.status_code

  response_parameters = {
      "method.response.header.Access-Control-Allow-Origin" = "'*'"
      "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
      "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    }  
}

#######################################################################################

resource "aws_api_gateway_resource" "auth" { # /auth
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_rest_api.receipt_scanner.root_resource_id
  path_part = "auth"
}

resource "aws_api_gateway_resource" "login" { # /auth/login
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_resource.auth.id
  path_part = "login"
}
resource "aws_api_gateway_method" "login_post" { # /auth/login-POST
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.login.id
  http_method = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "login_post_lambda" { # Lambda Integration for POST
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.login.id
  http_method = aws_api_gateway_method.login_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.auth-api.invoke_arn
  
}
resource "aws_api_gateway_method" "login_options" { # /auth/login-OPTIONS(For CORS)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.login.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "login_options" { # Mock Integration for OPTIONS
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.login.id
  http_method = aws_api_gateway_method.login_options.http_method

  type = "MOCK"

  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_method_response" "login_options" { # Method Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.login.id
  http_method = aws_api_gateway_method.login_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}
resource "aws_api_gateway_integration_response" "login_options" { # Integration Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.login.id
  http_method = aws_api_gateway_method.login_options.http_method
  status_code = aws_api_gateway_method_response.login_options.status_code

  response_parameters = {
      "method.response.header.Access-Control-Allow-Origin" = "'*'"
      "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
      "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
  }
}


resource "aws_api_gateway_resource" "register" { # /auth/register
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_resource.auth.id
  path_part = "register"
}
resource "aws_api_gateway_method" "register_post" { # /auth/register-POST
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.register.id
  http_method = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "register_post_lambda" { # Lambda Integration for POST
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.register.id
  http_method = aws_api_gateway_method.register_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.auth-api.invoke_arn 
}
resource "aws_api_gateway_method" "register_options" { # /auth/register-OPTIONS(For CORS)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.register.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "register_options" { # Mock Integration for OPTIONS
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.register.id
  http_method = aws_api_gateway_method.register_options.http_method

  type = "MOCK"
  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_method_response" "register_options" { # Method Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.register.id
  http_method = aws_api_gateway_method.register_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}
resource "aws_api_gateway_integration_response" "register_options" { # Integration Response for OPTIONS
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.register.id
  http_method = aws_api_gateway_method.register_options.http_method
  status_code = aws_api_gateway_method_response.register_options.status_code

  response_parameters = {
      "method.response.header.Access-Control-Allow-Origin" = "'*'"
      "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
      "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    }
}


##############################################################################################
resource "aws_api_gateway_resource" "profile" { # /profile
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_rest_api.receipt_scanner.root_resource_id
  path_part = "profile"
}
resource "aws_api_gateway_method" "profile_get" { # /profile-GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.profile.id
  http_method = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  request_parameters = {
    "method.request.header.Authorization" = true  
  }
}
resource "aws_api_gateway_integration" "profile_get_lambda" { # Lambda Integration for GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.profile.id
  http_method = aws_api_gateway_method.profile_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.auth-api.invoke_arn 
}
resource "aws_api_gateway_method" "profile_put" { # /profile-PUT
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.profile.id
  http_method = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "profile_put_lambda" { # Lambda Integration for PUT
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.profile.id
  http_method = aws_api_gateway_method.profile_put.http_method
  
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.auth-api.invoke_arn 
}
resource "aws_api_gateway_method" "profile_options" { # /profile-OPTIONS(For CORS)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.profile.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method_response" "profile_options" { # Method Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.profile.id
  http_method = aws_api_gateway_method.profile_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }  
}
resource "aws_api_gateway_integration_response" "profile_options" { # Integration Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.profile.id
  http_method = aws_api_gateway_method.profile_options.http_method
  status_code = aws_api_gateway_method_response.profile_options.status_code

  response_parameters = {
      "method.response.header.Access-Control-Allow-Origin" = "'*'"
      "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,OPTIONS'"
      "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  }
}

#######################################################################################
resource "aws_api_gateway_resource" "receipts" { # /receipts
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_rest_api.receipt_scanner.root_resource_id
  path_part = "receipts"
}
resource "aws_api_gateway_method" "receipts_get" { # /receipts-GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.receipts.id
  http_method = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  request_parameters = {
    "method.request.header.Authorization" = true
  }
}
resource "aws_api_gateway_integration" "receipts_get_lambda" { # Lambda Integration for GET
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.receipts.id
  http_method = aws_api_gateway_method.receipts_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.receipt-api.invoke_arn
}
resource "aws_api_gateway_method" "receipts_options" { # /receipts-OPTIONS(For CORS)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.receipts.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_method_response" "receipts_options" { # Method Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.receipts.id
  http_method = aws_api_gateway_method.receipts_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }  
}
resource "aws_api_gateway_integration_response" "receipts_options" { # Integration Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.receipts.id
  http_method = aws_api_gateway_method.receipts_options.http_method
  status_code = aws_api_gateway_method_response.receipts_options.status_code

  response_parameters = {
      "method.response.header.Access-Control-Allow-Origin" = "'*'"
      "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
      "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
  }
}

#######################################################################################
resource "aws_api_gateway_resource" "upload" {  # /upload
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_rest_api.receipt_scanner.root_resource_id
  path_part = "upload"
}

resource "aws_api_gateway_resource" "presigned_url" { # /upload/presigned-url
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  parent_id = aws_api_gateway_resource.upload.id
  path_part = "presigned-url"
}
resource "aws_api_gateway_method" "presigned_url_post" { # /upload/presigned-url-POST
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.presigned_url.id
  http_method = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
  request_parameters = {
    "method.request.header.Authorization" = true
  }
}
resource "aws_api_gateway_integration" "presigned_url_post_lambda" { # Lambda Integration for POST
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.presigned_url.id
  http_method = aws_api_gateway_method.presigned_url_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri = aws_lambda_function.receipt-api.invoke_arn
}
resource "aws_api_gateway_method" "presigned_url_options" { # /upload/presigned-url-OPTIONS(For CORS)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.presigned_url.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "presigned_url_options" { # Mock Integration for OPTIONS
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.presigned_url.id
  http_method = aws_api_gateway_method.presigned_url_options.http_method

  type = "MOCK"

  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}
resource "aws_api_gateway_method_response" "presigned_url_options" { # Method Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.presigned_url.id
  http_method = aws_api_gateway_method.presigned_url_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  } 
}
resource "aws_api_gateway_integration_response" "presigned_url_options" { # Integration Response for OPTIONS (CORS Headers)
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  resource_id = aws_api_gateway_resource.presigned_url.id
  http_method = aws_api_gateway_method.presigned_url_options.http_method
  status_code = aws_api_gateway_method_response.presigned_url_options.status_code

  response_parameters = {
      "method.response.header.Access-Control-Allow-Origin" = "'*'"
      "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
      "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    }
}

#######################################################################################
resource "aws_api_gateway_deployment" "receipt-scanner-api" {
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  depends_on = [
    aws_api_gateway_integration.metrics_get_lambda,
    aws_api_gateway_integration.metrics_options,
    aws_api_gateway_integration.monthly_get_lambda,
    aws_api_gateway_integration.monthly_options,
    aws_api_gateway_integration.patterns_get_lambda,
    aws_api_gateway_integration.patterns_options,
    aws_api_gateway_integration.summary_get_lambda,
    aws_api_gateway_integration.summary_options,
    aws_api_gateway_integration.login_post_lambda,
    aws_api_gateway_integration.login_options,
    aws_api_gateway_integration.register_post_lambda,
    aws_api_gateway_integration.register_options,
    aws_api_gateway_integration.profile_get_lambda,
    aws_api_gateway_integration.profile_put_lambda,
    aws_api_gateway_integration.profile_options,
    aws_api_gateway_integration.receipts_get_lambda,
    aws_api_gateway_integration.receipts_options,
    aws_api_gateway_integration.presigned_url_post_lambda,
    aws_api_gateway_integration.presigned_url_options
  ]
}
resource "aws_api_gateway_stage" "prod" {
  stage_name = "prod"
  rest_api_id = aws_api_gateway_rest_api.receipt_scanner.id
  deployment_id = aws_api_gateway_deployment.receipt-scanner-api.id
}
