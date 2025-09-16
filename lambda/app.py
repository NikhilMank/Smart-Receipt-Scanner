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
    """Return merchant, purchase_date, purchase_time, total_amount, and category from OCR text."""

    # Merchant: look for company name patterns
    merchant = ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines:
        # Skip lines with too many numbers, but allow some
        if (re.search(r"[A-Za-z]{3,}", line) and 
            not re.search(r"\d{5,}", line) and
            not re.search(r"(?:Tel|UID|Datum|Uhrzeit)", line, re.IGNORECASE)):
            merchant = line
            break

    # Date: German format patterns (DD.MM.YYYY)
    date_patterns = [
        r"(?:Datum|Date)\s*[:\-]?\s*(\d{1,2}\.\d{1,2}\.\d{4})",  # Datum: 16.08.2025
        r"\b(\d{1,2}\.\d{1,2}\.\d{4})\b",  # 16.08.2025
        r"\b(\d{4}-\d{1,2}-\d{1,2})\b",  # 2025-08-16
        r"TSE-Start:\s*(\d{4}-\d{2}-\d{2})",  # TSE-Start: 2025-08-16
    ]
    found_date = ""
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            found_date = match.group(1)
            break

    # Try to normalize to ISO YYYY-MM-DD
    parsed_date = ""
    if found_date:
        date_formats = [
            "%d.%m.%Y",  # German format
            "%Y-%m-%d",  # ISO format
        ]
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(found_date, fmt).date().isoformat()
                break
            except Exception:
                pass
    if not parsed_date:
        parsed_date = found_date

    # Time: German format patterns
    time_patterns = [
        r"(?:Uhrzeit|Zeit)\s*[:\-]?\s*(\d{1,2}:\d{2}(?::\d{2})?)",  # Uhrzeit: 11:42:11
        r"AS-Zeit\s+\d{2}\.\d{2}\.\s+(\d{1,2}:\d{2})",  # AS-Zeit 16.08. 11:42
        r"\b(\d{1,2}:\d{2}(?::\d{2})?)\s+Uhr\b",  # 11:42:11 Uhr
    ]
    found_time = ""
    for pattern in time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            found_time = match.group(1)
            break

    # Total amount: German receipt patterns
    amt_patterns = [
        r"SUMME\s+EUR\s+(\d+,\d{2})",  # SUMME EUR 4,56
        r"Betrag\s+EUR\s+(\d+,\d{2})",  # Betrag EUR 4,56
        r"Gesamtbetrag\s+[\d,]+\s+[\d,]+\s+(\d+,\d{2})",  # Gesamtbetrag line
        r"(?:Total|Gesamt)\s*[:\-]?\s*EUR?\s*(\d+,\d{2})",  # Total EUR 4,56
        r"EUR\s+(\d+,\d{2})(?:\s|$)",  # EUR 4,56 at end
    ]
    total_amount = ""
    for pattern in amt_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            total_amount = match.group(1)
            break

    # Category: determine based on merchant name
    category_mapping = {
        "grocery": ["REWE", "EDEKA", "ALDI", "LIDL", "KAUFLAND", "NETTO", "PENNY", "REAL"],
        "restaurant": ["MCDONALD", "DOMINOS", "BURGER KING", "KFC", "SUBWAY", "PIZZA", "RESTAURANT", "CAFE", "BAR"],
        "pharmacy": ["APOTHEKE", "PHARMACY", "DM", "ROSSMANN"],
        "gas_station": ["SHELL", "ARAL", "ESSO", "BP", "TOTAL", "TANKSTELLE"],
        "clothing": ["H&M", "ZARA", "C&A", "PRIMARK", "NIKE", "ADIDAS"],
        "electronics": ["MEDIA MARKT", "SATURN", "CONRAD", "CYBERPORT", "APPLE"],
        "other": []
    }
    
    category = "other"  # default
    merchant_upper = merchant.upper()
    for cat, keywords in category_mapping.items():
        if any(keyword in merchant_upper for keyword in keywords):
            category = cat
            break

    return {
        "merchant": merchant,
        "purchase_date": parsed_date,
        "purchase_time": found_time,
        "total_amount": total_amount,
        "category": category
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
            text_output = "\n".join([pytesseract.image_to_string(page, lang='deu+eng') for page in pages])
        else:
            print("Processing image...")
            img = Image.open(io.BytesIO(file_bytes))
            if img.width > 2000 or img.height > 2000:
                print("Resizing large image...")
                img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            print(f"Image size: {img.width}x{img.height}")
            print("Running tesseract with German language support...")
            # Use German + English for better accuracy on German receipts
            text_output = pytesseract.image_to_string(img, lang='deu+eng', timeout=60)
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
                "purchase_time": fields["purchase_time"],
                "total_amount": fields["total_amount"],
                "category": fields["category"],
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
