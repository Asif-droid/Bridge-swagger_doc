from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user details
    ---
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: A mock response with user data
        content:
          application/json:
            example:
              id: 1
              name: "John Doe"
              email: "john@example.com"
    """
    return jsonify({"id": user_id, "name": "John Doe", "email": "john@example.com"})

if __name__ == '__main__':
    app.run(debug=True)
