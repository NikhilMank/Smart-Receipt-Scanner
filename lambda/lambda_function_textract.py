import json
import boto3
import uuid
from datetime import datetime

s3 = boto3.client("s3")
textract = boto3.client("textract")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Receipts")

def lambda_handler(event, context):
    print("Event:", json.dumps(event, indent=2))
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    print(f"Processing file: {key} from bucket: {bucket}")

    # Use Textract for OCR (supports images and PDFs)
    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    
    # Extract text from Textract response
    text_output = ""
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            text_output += block['Text'] + "\n"
    
    print("Extracted text:", text_output)

    # Save to DynamoDB
    receipt_id = str(uuid.uuid4())
    table.put_item(
        Item={
            "receipt_id": receipt_id,
            "file_name": key,
            "raw_text": text_output,
            "upload_date": datetime.utcnow().isoformat()
        }
    )

    return {"status": "success", "receipt_id": receipt_id}