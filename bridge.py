from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import base64
import os
import uuid

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "Base64 Image Upload API"})
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/upload-image/", methods=["POST"])
def upload_image():
    """
    Upload an image in base64 format
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            image_base64:
              type: string
              description: Base64 encoded image
    responses:
      200:
        description: Image saved successfully
        schema:
          type: object
          properties:
            message:
              type: string
            file_path:
              type: string
      400:
        description: Invalid base64 data
    """
    try:
        data = request.get_json()
        image_base64 = data.get("image_base64")
        if not image_base64:
            return jsonify({"error": "Missing image_base64 field"}), 400
        
        image_bytes = base64.b64decode(image_base64)
        file_name = f"{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        
        return jsonify({"message": "Image saved successfully", "file_path": file_path})
    except Exception as e:
        return jsonify({"error": f"Invalid base64 data: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(debug=True)
