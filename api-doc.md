# API Documentation

## Overview
This API enables users to upload documents for processing and later check their status. It supports image files (PNG, JPG, JPEG) and various document types.

## Base URL
http://localhost:5000


## Authentication
All requests require an API key in the `Authorization` header.

---
## Endpoints

### 1. Upload Document
**Endpoint:** `POST /doc-upload`

**Headers:**
- `Authorization`: API Key (required)

**Form Data:**
- `file`: The document file (PNG, JPG, JPEG). Resolustion of the image must be in this range (1500-1700)x(2000-2600).
- `file_type`: The type of document (SALARY_CERTIFICATE, PAY_SLIP, JOB_ID, TRADE_LICENSE, OWNERSHIP_DOCUMENTS)

**Responses:**
- `200 OK`: Document uploaded successfully, processing started.
```json {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Document is being processed. Please check status after a while"
}
```
- `400 Bad Request`: Missing or invalid parameters.
- `401 Unauthorized`: API key is missing or invalid.
- `406 Not Acceptable`: Unsupported document type.
- `415 Unsupported Media Type`: File format not supported.

---
### 2. Check Document Status
**Endpoint:** `GET /doc-status/{request_id}`

**Headers:**
- `Authorization`: API Key (required)

**Path Parameter:**
- `request_id`: The unique ID returned when uploading a document.

**Responses:**
- `200 OK`: Processing completed, document data returned.
 Example Per Document Type:
 . JOB_ID
 ``` json
    {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "data": {
            "Name": "Md. Shahin Alam",
            "Company Name": "Innovative Solutions Ltd.",
            "Employee Id no": "EMP123456",
            "Company Email Id": "shahin.alam@innovativesolutions.com.bd",
            "Company Address": "Block A, 4th Floor, House 8, Dhanmondi, Dhaka-1205, Bangladesh"
        }
    }
 ```
 PAY_SLIP
 ``` json
    {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "data": {
            "Name of A/C Holder": "Fatema Begum",
            "Company Name": "GreenTech Innovations Ltd.",
            "Company Address": "Plot 12, Sector 7, Uttara, Dhaka-1230, Bangladesh",
            "Email": "fatema.begum@greentech.com.bd",
            "Date of Joining": "2023-08-15",
            "Designation": "Project Manager",
            "Department": "Operations",
            "Total Earnings": 95000
        }
    }
 ```
 SALARY_CERTIFICATE
 ``` json
    {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "data": {
            "Name of A/C Holder": "Md. Rahim Uddin",
            "Company Name": "Bangla Tech Solutions Ltd.",
            "Company Address": "House 45, Road 10, Banani, Dhaka-1213, Bangladesh",
            "Contact No": "+880 1555-123456",
            "Email": "rahim.uddin@banglatech.com.bd",
            "Designation": "Senior Software Developer",
            "Department": "IT & Development",
            "Basic salary amount": 60000,
            "Total salary amount": 75000
        }
    }

 ```
 TRADE_LICENSE
 ``` json
    {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "data": {
            "License No": "LN123456789",
            "NID No": "1234567890123456",
            "Owner Name": "Kazi Mohammad Karim",
            "Father's Name": "Kazi Abdul Majid",
            "Mother's Name": "Kazi Rokeya Begum",
            "Spouse Name": "Mst. Nafisa Karim",
            "Permanent Address": "Village Chotto, Upazila Baghair, District Narail, Bangladesh",
            "Current Address": "House 45, Road 10, Gulshan-2, Dhaka-1212, Bangladesh",
            "Business Name": "Karim & Sons Trading",
            "Business Address": "Shop 25, Market Road, Mohammadpur, Dhaka-1207, Bangladesh",
            "Business Type": "Wholesale Distribution",
            "Expiry Date": "2026-05-30"
        }
    }
 ```

- `202 Accepted`: Document is still being processed.
``` json
    {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "processing"
    }

```
- `401 Unauthorized`: API key is missing or invalid.
- `404 Not Found`: Request ID not found.
- `503 Service Unavailable`: Service unavailable.

---
## Swagger Documentation
The API is documented using Swagger.
- Swagger UI: [http://localhost:5000/api/docs](./swagger_doc.yml)
<!-- - Swagger JSON: [http://localhost:5000/swagger.json](http://localhost:5000/swagger.json) -->
