import os
import uuid
import time
import threading
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# In-memory storage for request status (simulating database)
request_store = {}

VALID_FILE_TYPES = {"SALARY_CERTIFICATE", "PAY_SLIP", "JOB_ID", "TRADE_LICENSE", "OWNERSHIP_DOCUMENTS"}

# Swagger UI Configuration
SWAGGER_URL = "/api/docs"  # Swagger UI URL
API_URL = "/swagger.json"   # Swagger JSON URL

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

API_KEY="123"

def process_document(request_id):
    """Simulate document processing with a delay."""
    time.sleep(100)  # Simulating processing time
    request_store[request_id]["status"] = "completed"
    request_store[request_id]["data"] = {
        "key_1": "value_1",
        "key_2": "value_2",
        "key_3": "value_3"
    }

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
def allowed_file(filename):
    """Check if file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/doc-upload", methods=["POST"])
def upload_document():
    """Upload a document and return a unique request ID."""
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    if not auth_header or auth_header != API_KEY:
        return jsonify({"message": "API key is required"}), 401

    if "file" not in request.files or "file_type" not in request.form:
        return jsonify({"message": "Missing required parameters"}), 400

    file = request.files["file"]
    file_type = request.form["file_type"]

    if file_type not in VALID_FILE_TYPES:
        return jsonify({"message": "Document type not supported"}), 406

    if file.filename == "":
        return jsonify({"message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "Only supported media is base64 encoded images (PNG, JPG, JPEG)"}), 415

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Generate a unique request_id
    request_id = str(uuid.uuid4())
    request_store[request_id] = {"status": "processing", "data": None}

    # Start processing in a separate thread
    threading.Thread(target=process_document, args=(request_id,)).start()

    return jsonify({
        "request_id": request_id,
        "message": "Document is being processed. Please check status after a while"
    }), 200


@app.route("/doc-status/<string:request_id>", methods=["GET"])
def get_status(request_id):
    """Get the processing status of an uploaded document."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != API_KEY :
        return jsonify({"message": "Authorization token is required"}), 401

    if request_id not in request_store:
        return jsonify({"error": "Request ID not found"}), 404

    status_info = request_store[request_id]

    if status_info["status"] == "processing":
        return jsonify({
            "request_id": request_id,
            "status": "processing"
        }), 202

    return jsonify({
        "request_id": request_id,
        "status": "completed",
        "data": status_info["data"]
    }), 200

@app.route("/swagger.json")
def swagger_json():
    """Return the OpenAPI specification."""
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "Document Processing API",
            "description": "API to upload documents and check their processing status",
            "version": "1.0.0"
        },
        "paths": {
            "/doc-upload": {
                "post": {
                    "summary": "Upload a document",
                    "description": "Uploads a document and returns a request ID",
                    "parameters": [
                        {
                            "name": "Authorization",
                            "in": "header",
                            "required": True,
                            "type": "string",
                            "description": "Bearer token for authentication"
                        },
                        {
                            "name": "file",
                            "in": "formData",
                            "required": True,
                            "type": "file",
                            "description": "Document file to be uploaded"
                        },
                        {
                            "name": "file_type",
                            "in": "formData",
                            "required": True,
                            "type": "string",
                            "enum": list(VALID_FILE_TYPES),
                            "description": "Type of document"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "request_id": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        },
                        "406": {
                            "description": "Document type not supported",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "request_id": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        },
                        "415": {
                            "description": "Unsupported Media Type",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "request_id": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        },
                        "429": {
                            "description": "Too Many Requests",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "request_id": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "/doc-status/{request_id}": {
                "get": {
                    "summary": "Get processing status",
                    "description": "Check the processing status of an uploaded document",
                    "parameters": [
                        {
                            "name": "request_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "Unique request ID"
                        },
                        {
                            "name": "Authorization",
                            "in": "header",
                            "required": True,
                            "type": "string",
                            "description": "Bearer token for authentication"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Processing complete",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "request_id": {"type": "string"},
                                    "status": {"type": "string"},
                                    "data": {"type": "object"}
                                }
                            }
                        },
                        "202": {
                            "description": "Processing, data not ready yet",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "request_id": {"type": "string"},
                                    "status": {"type": "string"}
                                }
                            }
                        },
                        "404": {"description": "Request ID not found",
                                "schema":{
                                    "type": "object",
                                    "properties":{
                                        "request_id":{"type": "string"},
                                        "status":{"type": "string"}
                                        
                                    }
                                
                                }
                            },
                        "503": {"description": "Service unavailable",
                                "schema":{
                                    "type": "object",
                                    "properties":{
                                        "request_id":{"type": "string"},
                                        "status":{"type": "string"}
                                        
                                    }
                                
                                }
                            }
                    }
                }
            }
        }
    })

if __name__ == "__main__":
    app.run(debug=True)
