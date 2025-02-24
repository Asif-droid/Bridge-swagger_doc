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
- `file_type`: The type of document (SALARY_CERTIFICATE, PAY_SLIP, JOB_ID, etc.)

**Responses:**
- `200 OK`: Document uploaded successfully, processing started.
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
- `202 Accepted`: Document is still being processed.
- `401 Unauthorized`: API key is missing or invalid.
- `404 Not Found`: Request ID not found.
- `503 Service Unavailable`: Service unavailable.

---
## Swagger Documentation
The API is documented using Swagger.
- Swagger UI: [http://localhost:5000/api/docs](./swagger_doc.yml)
<!-- - Swagger JSON: [http://localhost:5000/swagger.json](http://localhost:5000/swagger.json) -->
