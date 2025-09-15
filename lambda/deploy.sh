#!/bin/bash

# Install tesseract (required for pytesseract)
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils

# Create deployment package
mkdir -p package
cd package

# Install Python dependencies
pip install -r ../requirements.txt -t .

# Copy tesseract binary and data
mkdir -p usr/bin usr/share
cp /usr/bin/tesseract usr/bin/
cp -r /usr/share/tesseract* usr/share/

# Copy Lambda function
cp ../lambda_function.py .

# Create ZIP
zip -r ../lambda-deployment.zip .

cd ..
rm -rf package

echo "Created lambda-deployment.zip - upload to Lambda"