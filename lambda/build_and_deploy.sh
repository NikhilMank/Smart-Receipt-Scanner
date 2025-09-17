#!/bin/bash
#
# A bash script to build and deploy the docker image to AWS ECR
# and update the lambda function to use the new image.
#

# Set the AWS region
AWS_REGION="eu-central-1"

# Set the ECR repository name
AWS_ECR_REPO_NAME="receipt-ocr-lambda"

# Set the Lambda function name
LAMBDA_FUNCTION_NAME="receipt-ocr-container"

# Get the AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"

# Authenticate Docker to the ECR registry
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build the Docker image
docker build -t $AWS_ECR_REPO_NAME .

# Tag and Push the image to ECR
IMAGE_TAG="latest"
docker tag $AWS_ECR_REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPO_NAME:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPO_NAME:$IMAGE_TAG

# # Update the Lambda function to use the new image
# aws lambda update-function-code \
#     --function-name $LAMBDA_FUNCTION_NAME \
#     --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPO_NAME:$IMAGE_TAG \
#     --region $AWS_REGION