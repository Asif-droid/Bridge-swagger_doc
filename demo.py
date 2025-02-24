import os
import uuid
import time
import threading
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_swagger_ui import get_swaggerui_blueprint
import base64
from io import BytesIO
from PIL import Image
import json

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

def process_document(request_id,file_type):
    """Simulate document processing with a delay."""
    with open("example-data.json", "r", encoding="utf-8") as file:
        ex_data_all = json.load(file)
    
    ex_data=ex_data_all[file_type]
    print(ex_data)
    time.sleep(1)  # Simulating processing time
    request_store[request_id]["status"] = "completed"
    request_store[request_id][file_type] = ex_data
    # {
    #     "key_1": "value_1",
    #     "key_2": "value_2",
    #     "key_3": "value_3"
    # }

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
def allowed_file(filename):
    """Check if file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_extension(extension):
    """Check if the file extension is allowed."""
    return extension.lower() in ALLOWED_EXTENSIONS

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
    
    # data = request.get_json()
    # # print(data)
    # if not data or "file" not in data or "file_type" not in data:
    #     return jsonify({"message": "Missing required parameters"}), 400

    # base64_string = data["file"]
    # # print(base64_string)
    # file_type = data["file_type"]

    if file_type not in VALID_FILE_TYPES:
        return jsonify({"message": "Document type not supported"}), 406

    if file.filename == "":
        return jsonify({"message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "Only supported media is base64 encoded images (PNG, JPG, JPEG)"}), 415

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    try:
        image = Image.open(file)
        width, height = image.size
        print(f"Image resolution: {width}x{height}")
        # You can add additional checks for resolution if needed
        # For example, if you want to ensure the image is at least 800x600
        if (width > 1700 or width < 1500) or (height <2000 or height > 2600 ):
            return jsonify({"message": "Image resolution not within range. Accepted range (1500-1700)x(2000-2600)."}), 400
    except Exception as e:
        return jsonify({"message": f"Invalid image file: {str(e)}"}), 400

    
    # for base 64 encoded
    # try:
    #     # Decode the base64 string
    #     header, encoded = base64_string.split(",", 1) if "," in base64_string else ("", base64_string)
    #     decoded_image = base64.b64decode(encoded)

    #     # Determine file extension
    #     image = Image.open(BytesIO(decoded_image))
    #     ext = image.format.lower()

    #     if not allowed_file_extension(ext):
    #         return jsonify({"message": "Only PNG, JPG, and JPEG are allowed"}), 415

    #     # Generate a secure filename
    #     filename = f"{uuid.uuid4()}.{ext}"
    #     file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    #     # Save the image
    #     os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    #     image.save(file_path)

    # except Exception as e:
    #     return jsonify({"message": f"Invalid base64 image: {str(e)}"}), 400
    
    # Generate a unique request_id
    request_id = str(uuid.uuid4())
    request_store[request_id] = {"status": "processing"}

    # Start processing in a separate thread
    threading.Thread(target=process_document, args=(request_id,file_type)).start()

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
        "data": status_info
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
                        # {
                        #     "in": "body",
                        #     "name": "body",
                        #     "required": True,
                        #     "schema": {
                        #         "type": "object",
                        #         "properties": {
                        #             "file": {
                        #                 "type": "string",
                        #                 "description": "Base64 encoded image"
                        #                 },
                        #             "file_type" : {
                        #                 "type": "string",
                        #                 "enum": list(VALID_FILE_TYPES)
                        #             }
                        #         }
                        #     }
                        # }
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
                    # "requestBody": {
                    #     "required": True,
                    #     "content": {
                    #         "application/json": {
                    #             "schema": {
                    #                 "type": "object",
                    #                 "properties": {
                    #                     "file": {
                    #                         "type": "string",
                    #                         "description": "Base64-encoded image string (optionally prefixed with 'data:image/png;base64,')"
                    #                     },
                    #                     "file_type": {
                    #                         "type": "string",
                    #                         "enum": list(VALID_FILE_TYPES),
                    #                         "description": "Type of document (Only 'image' is allowed)"
                    #                     }
                    #                 },
                    #                 "required": ["file", "file_type"]
                    #             }
                    #         }
                    #     }
                    # },
                    
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
                        },
                        "400": {
                            "description": "Bad Request",
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
