import json
import os
import io
import re
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

# --- NEW: simple field extractor ---------------------------------
def extract_fields(text: str) -> dict:
    """Return merchant, purchase_date, and total_amount from OCR text."""

    # Merchant: first non-empty line without a long digit run
    merchant = ""
    for line in (l.strip() for l in text.splitlines() if l.strip()):
        if re.search(r"[A-Za-z]", line) and not re.search(r"\d{5,}", line):
            merchant = line
            break

    # Date: common patterns (2025-09-15, 15/09/2025, Sep 15 2025…)
    date_patterns = [
        r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[ .-]?\d{1,2}[, ]+\d{4}\b",
    ]
    found_date = next((m.group(0) for p in date_patterns
                       for m in [re.search(p, text, re.IGNORECASE)] if m), "")

    # Try to normalize to ISO YYYY-MM-DD
    parsed_date = ""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y",
                "%d/%m/%y", "%d-%m-%y"):
        try:
            parsed_date = datetime.strptime(found_date, fmt).date().isoformat()
            break
        except Exception:
            pass
    if not parsed_date:
        parsed_date = found_date  # keep raw if parsing fails

    # Total amount: look for "Total", "Amount", etc.
    amt_match = re.search(
        r"(?:Total|Amount|Grand|Balance)\s*[:\-]?\s*([$€£]?\s?\d+[.,]?\d{0,2})",
        text, re.IGNORECASE)
    total_amount = amt_match.group(1).replace(" ", "") if amt_match else ""

    return {
        "merchant": merchant,
        "purchase_date": parsed_date,
        "total_amount": total_amount
    }
# -----------------------------------------------------------------

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

    # --- NEW: extract structured fields ---------------------------
    fields = extract_fields(text_output)
    print("Parsed fields:", fields)
    # ---------------------------------------------------------------

    try:
        print("Saving to DynamoDB...")
        receipt_id = str(uuid.uuid4())
        table.put_item(
            Item={
                "receipt_id": receipt_id,
                "file_name": key,
                "raw_text": text_output,
                "upload_date": datetime.utcnow().isoformat(),
                "merchant": fields["merchant"],
                "purchase_date": fields["purchase_date"],
                "total_amount": fields["total_amount"],
            }
        )
        print("Successfully saved to DynamoDB")
    except Exception as e:
        print(f"Error saving to DynamoDB: {e}")
        return {"status": "error", "message": f"Database save failed: {str(e)}"}

    return {
        "status": "success",
        "receipt_id": receipt_id,
        "parsed": fields
    }
