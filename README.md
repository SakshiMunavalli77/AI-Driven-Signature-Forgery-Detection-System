# AI-Driven Signature Forgery Detection System

## Project Overview

The AI-Driven Signature Forgery Detection System is a web-based application that uses Deep Learning and Computer Vision techniques to verify handwritten signatures and detect forgeries. The system employs a Siamese Neural Network with a ResNet50 backbone to compare two signature images and determine whether they belong to the same person.

The application allows users to upload signatures, perform verification, view prediction results, and maintain prediction history through an interactive web interface.

---

## Objectives

* Detect forged signatures using Artificial Intelligence.
* Compare two signature images and measure similarity.
* Provide genuine/forged prediction with confidence score.
* Maintain prediction history for authenticated users.
* Provide a secure and user-friendly web application.

---

## Technologies Used

### Programming Language

* Python

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Flask

### Database

* MongoDB

### Deep Learning Framework

* PyTorch

### Image Processing

* PIL (Pillow)
* Torchvision

### Authentication

* Flask-Login
* Flask-Bcrypt

### Version Control

* Git
* GitHub

---

## System Architecture

### User Layer

* User Registration
* User Login
* Signature Upload

### Application Layer

* Flask Backend
* Authentication Module
* Prediction Module

### AI Processing Layer

* Image Preprocessing
* ResNet50 Feature Extraction
* Siamese Neural Network Verification

### Database Layer

* MongoDB
* User Records
* Prediction History

### Output Layer

* Genuine/Forged Prediction
* Confidence Score
* Distance Score
* History Dashboard

---

## Workflow

1. User registers and logs in.
2. User uploads two signature images.
3. Images are preprocessed and resized.
4. ResNet50 extracts signature features.
5. Siamese Network generates embeddings.
6. Euclidean Distance is calculated.
7. Distance is compared with threshold value.
8. Genuine or Forged result is generated.
9. Result is stored in MongoDB.
10. Prediction history is displayed.

---

## Dataset

The system uses an offline handwritten signature dataset containing:

* Genuine Signatures
* Forged Signatures

### Preprocessing

* Image Resizing
* Normalization
* Data Augmentation
* RGB Conversion

---

## Installation Steps

### Clone Repository

```bash
git clone https://github.com/SakshiMunavalli77/AI-Driven-Signature-Forgery-Detection-System.git
```

### Move to Project Directory

```bash
cd AI-Driven-Signature-Forgery-Detection-System
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure MongoDB

Ensure MongoDB is running locally:

```bash
mongodb://localhost:27017/signature_forgery_db
```

### Run Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Features

* User Registration and Login
* Secure Authentication
* Signature Upload
* AI-Based Signature Verification
* Genuine/Forged Prediction
* Confidence Score Generation
* Prediction History
* MongoDB Integration

---

## Sample Output

### Genuine Signature

Result: Genuine Signature

Confidence: High

Distance: Low

### Forged Signature

Result: Forged Signature

Confidence: High

Distance: High

---

## Future Enhancements

* Mobile Application Integration
* Cloud Deployment
* Multi-Signature Verification
* Real-Time Signature Verification
* Advanced Deep Learning Models
* Admin Dashboard
* Report Generation Module

---

## Author

**Sakshi Basavaraj Munavalli**

Master of Computer Applications (MCA)


---

## License

This project is developed for academic and educational purposes.
