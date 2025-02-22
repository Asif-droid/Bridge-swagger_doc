import os
import uuid
import time
import threading
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flasgger import Swagger

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

swagger = Swagger(app)
# In-memory storage for request status (simulating database)
request_store = {}

VALID_FILE_TYPES = {"SALARY_CERTIFICATE", "PAY_SLIP", "JOB_ID", "TRADE_LICENSE", "OWNERSHIP_DOCUMENTS"}

def process_document(request_id):
    """Simulate document processing with a delay."""
    time.sleep(10)  # Simulating processing time
    request_store[request_id]["status"] = "completed"
    request_store[request_id]["data"] = {
        "key_1": "value_1",
        "key_2": "value_2",
        "key_3": "value_3"
    }

@app.route("/api/upload", methods=["POST"])
def upload_document():
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    if not auth_header:
        return jsonify({"message": "API key is required"}), 401

    if "file" not in request.files or "file_type" not in request.form:
        return jsonify({"message": "Missing required parameters"}), 400

    file = request.files["file"]
    file_type = request.form["file_type"]

    if file_type not in VALID_FILE_TYPES:
        return jsonify({"message": "Document type not supported"}), 406

    if file.filename == "":
        return jsonify({"message": "No file selected"}), 400

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


@app.route("/api/status/<string:request_id>", methods=["GET"])
def get_status(request_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        print(auth_header)
        return jsonify({"message": "Authorization token is required"}), 401

    if request_id not in request_store:
        return jsonify({"error": "Request ID not found"}), 404

    status_info = request_store[request_id]

    if status_info["status"] == "processing":
        return jsonify({
            "request_id": request_id,
            "status": "processing, data not ready yet"
        }), 204

    return jsonify({
        "request_id": request_id,
        "status": "completed",
        "data": status_info["data"]
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
