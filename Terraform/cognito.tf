resource "aws_cognito_user_pool" "receipt_scanner" {
  name = "receipt-scanner-user-pool"

  auto_verified_attributes = ["email"]
  
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = false
  }

  schema {
    name                = "name"
    attribute_data_type = "String"
    required            = false
    mutable             = true
  }
}

resource "aws_cognito_user_pool_client" "receipt_scanner" {
  name         = "receipt-scanner"
  user_pool_id = aws_cognito_user_pool.receipt_scanner.id

  explicit_auth_flows = [
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  generate_secret = false
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.receipt_scanner.id
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.receipt_scanner.id
}