import pathlib
import os

# Configuration settings
AUTH_TOKEN = "YourSecretToken!;%:?*()_+"
PATH_TO_ANY_DESK = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe")
PATH_TO_PW_FILE = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\file.txt")
NGROK_AUTH_TOKEN = '2ETJzIGCEuQ8aJaGWju3nA4sswz_6xeXM7qFqhNvBXCAL8pKZ'
MONGO_URI = "mongodb+srv://admin:WIyniFnVBpcbG1pJ@cluster0.aaaafpm.mongodb.net/?retryWrites=true&w=majority"

os.environ['NGROK_AUTHTOKEN'] = NGROK_AUTH_TOKEN

UPDATE_PW_POWERSHELL_COMMAND = f"""
$newPassword = Get-Content "{PATH_TO_PW_FILE}"
echo $newPassword | anydesk --set-password;
Start-Sleep -Seconds 1;
$serviceName="AnyDesk";
if((Get-Service -Name $serviceName).Status -eq "Running")
{{Restart-Service -Name $serviceName;}};
echo "Success"
"""
