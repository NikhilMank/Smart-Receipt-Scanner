# Table for Receipt Data
resource "aws_dynamodb_table" "receipts" {
    name = "Receipts"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "receipt_id"
    attribute {
        name = "receipt_id"
        type = "S"
    }
    attribute {
        name = "category"
        type = "S"
    }
    attribute {
      name = "file_name"
      type = "S"
    }
    attribute {
        name = "merchant"
        type = "S"
    }
    attribute {
        name = "purchase_date"
        type = "S"
    }
    attribute {
        name = "purchase_time"
        type = "S"
    }
    attribute {
        name = "raw_text"
        type = "S"
    }
    attribute {
        name = "total_amount"
        type = "S"
    }
    attribute {
        name = "upload_date"
        type = "S"
    }
    attribute {
        name = "user_id"
        type = "S"
    }      
}


# Table to Store Users
resource "aws_dynamodb_table" "users" {
  name = "Users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "user_id"
  attribute {
    name = "user_id"
    type = "S"
  }
  attribute {
    name = "created_at"
    type = "S"
  }
  attribute {
    name = "email"
    type = "S"
  }
  attribute {
    name = "name"
    type = "S"
  }
  attribute {
    name = "monthly_budget"
    type = "N"
  }  
}
