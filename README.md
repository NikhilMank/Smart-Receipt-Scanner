# 📄 Smart Receipt Scanner & Organizer

## 📌 Overview
Managing expenses from physical receipts is tedious and error-prone. People often lose receipts or spend time manually entering details into spreadsheets.  
This project aims to build a **cloud-native, AI-powered receipt management system** that automatically extracts, categorizes, and visualizes spending data.

The solution is implemented using **AWS serverless services** to ensure scalability, low cost, and ease of deployment.

---

## 🎯 Project Goals
- Upload receipt images via a simple web interface.
- Automatically extract key details:
  - Store name
  - Date
  - Total amount
- Categorize expenses (e.g., groceries, travel, dining).
- Allow manual edits in case of OCR errors.
- View all receipts in a searchable dashboard.
- Analyze spending trends with **visual dashboards**.

---

## ☁️ AWS Services Used
| AWS Service              | Purpose |
|--------------------------|---------|
| **Amazon S3**            | Store uploaded receipt images. |
| **AWS Lambda**           | Serverless backend logic (parsing, categorization, data storage). |
| **Amazon DynamoDB**      | Store structured receipt data (NoSQL). |
| **Amazon API Gateway**   | Provide REST APIs for frontend integration. |
| **AWS Glue**             | ETL pipeline to export data from DynamoDB to S3. |
| **Amazon QuickSight**    | Create dashboards for spending analysis (by month, category, store). |
| **Amazon CloudFront** *(optional)* | Serve frontend with HTTPS and low latency. |
| **Amazon Cognito** *(optional)* | User authentication for secure data access. |

---

## 🖥️ Other Tools
- **Frontend:** HTML/CSS/JavaScript (or React) for upload & dashboard UI.  
- **Tesseract OCR:** For text extraction from receipt images.  
- **Python:** For AWS Lambda functions.
- **Regex / Rule-based Parsing:** To improve field extraction (store, date, total).  
- **GitHub:** Version control and documentation.  

---

## 📊 Expected Outcomes
- A working cloud-based application where users can:
  - Upload receipts
  - View structured receipt data
  - Edit incorrect fields
- Automatic categorization of expenses incase the user does not provide one.
- QuickSight dashboards with:
  - Spending by month
  - Spending by store
  - Spending by category
- Demo workflow: *Upload → Extract → Store → Edit → Analyze*

## 🚀 Stretch Goals
- Add login/authentication with **Amazon Cognito**.  
- Email/SMS notifications when a new receipt is processed (via **Amazon SNS**).  
- Export receipts to CSV.  
- Use Amazon Comprehend or ML model for improved entity extraction.  

---