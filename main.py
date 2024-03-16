import os
import socket
import psutil
import GPUtil

import ngrok
import random
import string
import pathlib
import subprocess

import pymongo
from flask import Flask, request, jsonify

app = Flask(__name__)

AUTH_TOKEN = "YourSecretToken"
PATH_TO_ANY_DESK = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
PATH_TO_PW_FILE = r"C:\Program Files (x86)\AnyDesk\file.txt"
PATH_TO_ANY_DESK = pathlib.Path(PATH_TO_ANY_DESK)
PATH_TO_PW_FILE = pathlib.Path(PATH_TO_PW_FILE)
TASK_NAME = "UpdateAnyDeskPassword"
os.environ['NGROK_AUTHTOKEN'] = '2ETJzIGCEuQ8aJaGWju3nA4sswz_6xeXM7qFqhNvBXCAL8pKZ'
MONGO_URI = "mongodb+srv://admin:WIyniFnVBpcbG1pJ@cluster0.aaaafpm.mongodb.net/?retryWrites=true&w=majority"


def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def get_system_info():
    """
    Returns a dictionary containing system information including CPU and GPU details.
    """
    # Get the machine name
    machine_name = socket.gethostname()

    # Get CPU information
    cpu_info = psutil.cpu_freq()
    cpu = f"{psutil.cpu_count(logical=False)} Physical, {psutil.cpu_count(logical=True)} Logical, {cpu_info.max:.2f}MHz Max Frequency"

    # Attempt to get GPU information, default to None if GPUUtil is not applicable
    gpu = "Not Found"
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = ", ".join([f"{gpu.name}" for gpu in gpus])

    return {"machine_name": machine_name, "cpu": cpu, "gpu": gpu}


def save_or_update_ngrok_url(url):
    """
    Saves or updates the ngrok URL in MongoDB with the machine identifier.
    """
    client = pymongo.MongoClient(MONGO_URI)
    db = client["new_database"]
    collection = db["nodes"]

    # Use the hostname as a simple identifier
    machine_id = socket.gethostname()
    system_info = get_system_info()

    # Attempt to update the document if it exists, otherwise insert a new one
    update_result = collection.update_one(
        {"machine_id": machine_id},
        {"$set": {"update_password_webhook": url, "cpu": system_info["cpu"], "gpu": system_info["gpu"]}},
        upsert=True
    )

    if update_result.matched_count > 0:
        print("Updated the ngrok URL for the existing machine ID.")
    else:
        print("Inserted a new document with the ngrok URL and machine ID.")

    client.close()


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


if __name__ == '__main__':
    listener = ngrok.forward(5000, authtoken_from_env=True)
    print(f"Ingress established at {listener.url()}")
    save_or_update_ngrok_url(listener.url())
    app.run(port=5000, debug=True)
