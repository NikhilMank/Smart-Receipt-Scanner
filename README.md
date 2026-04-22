# 📄 Receipt Scanner Multi-User System

## 📌 Overview
A **cloud-native, multi-user receipt management system** that automatically extracts, categorizes, and analyzes spending data from receipt images and PDFs. Built with AWS serverless architecture for scalability, security, and cost-effectiveness.

**🌐 Live Demo:** [http://receipt-scanner-frontend.s3-website.eu-central-1.amazonaws.com](http://receipt-scanner-frontend.s3-website.eu-central-1.amazonaws.com)

---

## ✨ Key Features

### 🔐 Multi-User Authentication
- Secure user registration and login with **AWS Cognito**
- JWT-based authentication with complete user data isolation
- Each user can only access their own receipts and data

### 📸 Advanced OCR Processing
- Support for both **images** (JPG, PNG) and **PDF** receipts
- **German + English** language support optimized for European receipts
- Advanced **image preprocessing** for enhanced accuracy:
  - Noise reduction and contrast enhancement
  - Binary thresholding with Otsu's method
  - Morphological operations for text cleanup
- Intelligent **merchant detection** for major German retailers (REWE, EDEKA, ALDI, ZARA, ACTION, etc.)
- **Smart field extraction** using regex patterns:
  - Store name and merchant identification
  - Purchase date and time (German formats)
  - Total amount with German number formatting
  - Automatic expense categorization

### 💰 Budget Management & Analytics
- **Monthly budget setting** with real-time tracking
- **Visual progress indicators** showing budget vs. spending
- **Category-wise expense breakdown** (grocery, restaurant, clothing, etc.)
- **Month filters** to analyze current and previous month spending
- **Interactive charts** and progress bars for data visualization

### 🗂️ Receipt Management
- **File upload** via upload button or camera capture
- **Automatic processing** triggered by S3 events
- **Receipt listing** displaying extracted data (merchant, date, amount, category)
- **Real-time updates** after processing completion

---

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│    │   AWS API Gateway│    │  Lambda Functions│
│   (S3 Static)   │◄──►│  + Cognito Auth  │◄──►│   (API + OCR)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   AWS Cognito    │    │   Amazon S3     │
                       │   User Pool      │    │ Receipt Storage │
                       └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   DynamoDB      │
                                               │ (Receipts/Users)│
                                               └─────────────────┘
```

---

## ☁️ AWS Services Used

| AWS Service              | Purpose |
|--------------------------|---------|
| **Amazon Cognito**       | User authentication, JWT token management, user pool |
| **AWS API Gateway**      | RESTful API endpoints with Cognito authorizer |
| **AWS Lambda**           | Serverless functions for API logic and OCR processing |
| **Amazon S3**            | Receipt file storage with event-driven processing |
| **Amazon DynamoDB**      | NoSQL database for receipts and user profile data |
| **Amazon ECR**           | Container registry for OCR Lambda deployment |
| **AWS CloudWatch**       | Logging and monitoring for all services |

---

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern JavaScript framework
- **Axios** - HTTP client for API communication
- **CSS3** - Responsive design and styling
- **Chart.js** - Data visualization for analytics

### Backend
- **Python 3.9** - OCR Lambda runtime
- **Node.js 18** - API Lambda runtime
- **Tesseract OCR** - Text extraction engine
- **OpenCV** - Image preprocessing
- **pdf2image** - PDF to image conversion

### Infrastructure
- **Docker** - Containerized OCR Lambda
- **AWS CLI** - Deployment and management
- **Git** - Version control

---

## 📊 Current Implementation Status

### ✅ Completed Features
- ✅ Multi-user authentication with AWS Cognito
- ✅ Secure file upload with S3 presigned URLs
- ✅ Advanced OCR processing with German language support
- ✅ Intelligent merchant detection and categorization
- ✅ User data isolation and security
- ✅ Budget management with visual analytics
- ✅ Responsive React frontend
- ✅ Real-time receipt processing
- ✅ CORS-compliant API endpoints
- ✅ Production deployment on AWS

### 🔄 Recent Improvements
- Enhanced OCR accuracy with image preprocessing
- Improved German receipt parsing patterns
- Better merchant detection for German stores
- Budget analytics with month filtering
- User profile management
- Frontend deployment to S3 static hosting

---

<!--
## 🚀 Getting Started

### Prerequisites
- AWS Account with appropriate permissions
- Node.js 18+ and Python 3.9+
- Docker for OCR Lambda deployment
- AWS CLI configured

### Quick Setup
1. **Clone the repository**
2. **Deploy AWS infrastructure** (Cognito, DynamoDB, S3, Lambda)
3. **Build and deploy OCR Lambda** container to ECR
4. **Configure API Gateway** with Cognito authorizer
5. **Deploy React frontend** to S3 static hosting
6. **Test the complete workflow**

*Detailed setup instructions available in PROJECT_DOCUMENTATION.md*
-->

---

## 📈 Performance & Scalability

- **Serverless Architecture**: Automatic scaling based on demand
- **Event-Driven Processing**: S3 triggers for efficient OCR processing
- **User Isolation**: Complete data separation for security
- **Cost-Effective**: Pay-per-use pricing model
- **High Availability**: Multi-AZ deployment with AWS managed services

---

## 🔮 Future Enhancements

- **Drag-and-Drop Upload**: Enhanced file upload interface
- **Receipt Image Display**: Show original receipt images in listing
- **Search & Filter**: Search receipts by merchant, date, or amount
- **Delete Functionality**: Remove receipts from the system
- **Mobile App**: React Native mobile application
- **Receipt Templates**: Support for more receipt formats
- **Export Features**: CSV/PDF export functionality
- **Advanced Analytics**: Machine learning for spending insights
- **Multi-Language**: Support for more European languages
- **Notifications**: Email alerts for budget limits
- **Receipt Sharing**: Team/family expense sharing features

---

## 👨💻 Author

Developed by **Nikhil Mankali**

---