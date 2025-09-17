#!/bin/bash
#
# Deploy the API Lambda function and create API Gateway
#

AWS_REGION="eu-central-1"
FUNCTION_NAME="receipt-api"
API_NAME="receipt-analytics-api"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"

# Create ZIP package for API Lambda
zip -r api-lambda.zip api_lambda.py

# Create or update Lambda function
echo "Creating/updating Lambda function..."
aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.12 \
    --role arn:aws:iam::$AWS_ACCOUNT_ID:role/ReceiptProcessor-role-y5lp12ms \
    --handler api_lambda.lambda_handler \
    --zip-file fileb://api-lambda.zip \
    --timeout 30 \
    --memory-size 256 \
    --region $AWS_REGION 2>/dev/null || \
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://api-lambda.zip \
    --region $AWS_REGION

# Create API Gateway
echo "Creating API Gateway..."
API_ID=$(aws apigateway create-rest-api \
    --name $API_NAME \
    --description "Receipt Analytics API" \
    --region $AWS_REGION \
    --query 'id' --output text)

echo "API Gateway ID: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region $AWS_REGION \
    --query 'items[0].id' --output text)

# Create /receipts resource
RECEIPTS_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part receipts \
    --region $AWS_REGION \
    --query 'id' --output text)

# Create /receipts/{id} resource
RECEIPT_ID_RESOURCE=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $RECEIPTS_ID \
    --path-part '{id}' \
    --region $AWS_REGION \
    --query 'id' --output text)

# Create /analytics resource
ANALYTICS_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part analytics \
    --region $AWS_REGION \
    --query 'id' --output text)

# Create /analytics/summary resource
SUMMARY_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ANALYTICS_ID \
    --path-part summary \
    --region $AWS_REGION \
    --query 'id' --output text)

# Create /analytics/monthly resource
MONTHLY_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ANALYTICS_ID \
    --path-part monthly \
    --region $AWS_REGION \
    --query 'id' --output text)

# Add GET methods and integrations
for RESOURCE_ID in $RECEIPTS_ID $RECEIPT_ID_RESOURCE $SUMMARY_ID $MONTHLY_ID; do
    # Create GET method
    aws apigateway put-method \
        --rest-api-id $API_ID \
        --resource-id $RESOURCE_ID \
        --http-method GET \
        --authorization-type NONE \
        --region $AWS_REGION

    # Create integration
    aws apigateway put-integration \
        --rest-api-id $API_ID \
        --resource-id $RESOURCE_ID \
        --http-method GET \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:function:$FUNCTION_NAME/invocations \
        --region $AWS_REGION
done

# Add Lambda permission for API Gateway
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id api-gateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$AWS_REGION:$AWS_ACCOUNT_ID:$API_ID/*/*" \
    --region $AWS_REGION

# Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region $AWS_REGION

echo "API deployed successfully!"
echo "API URL: https://$API_ID.execute-api.$AWS_REGION.amazonaws.com/prod"
echo ""
echo "Available endpoints:"
echo "GET /receipts - List all receipts"
echo "GET /receipts/{id} - Get specific receipt"
echo "GET /analytics/summary - Spending summary by category"
echo "GET /analytics/monthly - Monthly spending trends"