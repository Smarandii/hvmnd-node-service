from flask import Flask, request, jsonify
import subprocess
from .utils import generate_password
from .config import AUTH_TOKEN, PATH_TO_PW_FILE

app = Flask(__name__)


@app.route('/update_password', methods=['POST'])
def update_password():
    auth_token = request.headers.get('Authorization')
    if auth_token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    new_password = generate_password()
    with open(PATH_TO_PW_FILE, "w") as pwd_file:
        pwd_file.write(new_password)
    try:
        command = ["powershell.exe", "-ExecutionPolicy", "Unrestricted", "-File", "update_password.ps1"]
        process = subprocess.run(command, capture_output=True, text=True)
        if process.returncode == 0:
            return jsonify({"new_password": new_password})
        else:
            return jsonify({"error": "Failed to update password", "details": process.stderr}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to update password", "details": str(e)}), 500


@app.route('/restart_node', methods=['POST'])
def restart_node():
    auth_token = request.headers.get('Authorization')
    if auth_token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        command = ["powershell.exe", "-Command", "Restart-Computer -Force"]
        process = subprocess.run(command)
        if process.returncode == 0:
            return jsonify({"restarted": True}), 200
        else:
            return jsonify({"error": "Failed to restart node", "details": process.stderr}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to restart node", "details": str(e)}), 500


@app.route('/liveliness', methods=['GET'])
def liveliness():
    return jsonify({"alive": True}), 200
