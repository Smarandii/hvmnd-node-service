import sys

from flask import Flask, request, jsonify
import subprocess
import random
import string
import pathlib

app = Flask(__name__)

# Simple authentication token for demonstration purposes
# In production, use a more secure method for authentication
AUTH_TOKEN = "YourSecretToken"
PATH_TO_ANY_DESK = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
PATH_TO_PW_FILE = r"C:\Program Files (x86)\AnyDesk\file.txt"
PATH_TO_ANY_DESK = pathlib.Path(PATH_TO_ANY_DESK)
PATH_TO_PW_FILE = pathlib.Path(PATH_TO_PW_FILE)
TASK_NAME = "UpdateAnyDeskPassword"


def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


@app.route('/update_password', methods=['POST'])
def update_password():
    auth_token = request.headers.get('Authorization')
    if auth_token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    new_password = generate_password()

    # Write the new password to a secure location
    with open(PATH_TO_PW_FILE, "w") as pwd_file:
        pwd_file.write(new_password)

    # Trigger the scheduled task
    command = (
        f'$newPassword = Get-Content "{PATH_TO_PW_FILE}"'
        'echo $newPassword | anydesk --set-password;'
        'Start-Sleep -Seconds 1;'
        '$serviceName="AnyDesk";'
        'if((Get-Service -Name $serviceName).Status -eq "Running")'
        '{Restart-Service -Name $serviceName;}'
    )

    try:
        p = subprocess.Popen(
            [
                "powershell.exe",
                "-noprofile", "-c",
                r"""
                Start-Process -Verb RunAs -Wait powershell.exe -Args "
                  -noprofile -c Set-Location \`"$PWD\`"; & update_password.ps1
                  "
                """
            ],
            stdout=sys.stdout
        )
        p.communicate()

        return jsonify({"new_password": new_password, "return_code": p.returncode})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to update password", "details": str(e)}), 500


if __name__ == '__main__':
    # DO NOT run this app with debug=True in production!
    app.run(port=5000, debug=True)
