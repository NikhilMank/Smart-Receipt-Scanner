import json
import os
import io
import boto3
import uuid
from datetime import datetime
from urllib.parse import unquote_plus
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Receipts")

def lambda_handler(event, context):
    print("Event:", json.dumps(event, indent=2))
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = unquote_plus(record['s3']['object']['key'])
    print(f"Processing file: {key} from bucket: {bucket}")

    try:
        print("Getting S3 object...")
        obj = s3.get_object(Bucket=bucket, Key=key)
        file_bytes = obj['Body'].read()
        print(f"File size: {len(file_bytes)} bytes")
    except Exception as e:
        print(f"Error getting object: {e}")
        return {"status": "error", "message": str(e)}

    try:
        print("Starting OCR processing...")
        if key.lower().endswith(".pdf"):
            print("Processing PDF...")
            pages = convert_from_bytes(file_bytes)
            text_output = "\n".join([pytesseract.image_to_string(page) for page in pages])
        else:
            print("Processing image...")
            img = Image.open(io.BytesIO(file_bytes))
            
            if img.width > 2000 or img.height > 2000:
                print("Resizing large image...")
                img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            
            print(f"Image size: {img.width}x{img.height}")
            
            print("Running tesseract...")
            text_output = pytesseract.image_to_string(img, timeout=60)
            print("Tesseract completed successfully")
        
        print(f"OCR completed. Text length: {len(text_output)}")
        print("Extracted text:", text_output[:200] + "..." if len(text_output) > 200 else text_output)
    except Exception as e:
        print(f"Error during OCR: {e}")
        return {"status": "error", "message": f"OCR failed: {str(e)}"}

    try:
        print("Saving to DynamoDB...")
        receipt_id = str(uuid.uuid4())
        table.put_item(
            Item={
                "receipt_id": receipt_id,
                "file_name": key,
                "raw_text": text_output,
                "upload_date": datetime.utcnow().isoformat()
            }
        )
        print("Successfully saved to DynamoDB")
    except Exception as e:
        print(f"Error saving to DynamoDB: {e}")
        return {"status": "error", "message": f"Database save failed: {str(e)}"}

    return {"status": "success", "receipt_id": receipt_id}