from flask import Flask, request, jsonify
import subprocess
import random
import string

app = Flask(__name__)

# Simple authentication token for demonstration purposes
# In production, use a more secure method for authentication
AUTH_TOKEN = "YourSecretToken"
PATH_TO_ANY_DESK = "AnyDesk.exe"


def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


@app.route('/update_password', methods=['POST'])
def update_password():
    auth_token = request.headers.get('Authorization')
    if auth_token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    new_password = generate_password()
    command = [PATH_TO_ANY_DESK, '--set-password', new_password]

    try:
        subprocess.run(command)
        # In a real implementation, ensure this data is transmitted securely
        return jsonify({"new_password": new_password})
    except subprocess.CalledProcessError:
        return jsonify({"error": "Failed to update password"}), 500


if __name__ == '__main__':
    # DO NOT run this app with debug=True in production!
    app.run(port=5000, debug=True)
