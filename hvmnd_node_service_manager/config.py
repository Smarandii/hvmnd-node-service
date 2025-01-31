import pathlib

PATH_TO_ANY_DESK = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe")
PATH_TO_PW_FILE = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\file.txt")
PATH_TO_LOG_FILE = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\logs.log")
#HVMND_API_CLIENT_BASE_URL = "http://prod.hvmnd-api.freemyip.com/api/v1"
HVMND_API_CLIENT_BASE_URL = "http://localhost:9876/api/v1"
HVMND_API_TOKEN = "hvmnd-node-api-token"
ALERT_BOT_TOKEN = "6524183208:AAHXOGhNtuQ1mHis-3J9_tsd01ZI0CTIX60"
ADMIN_CHAT_ID = "231584958"
UPDATE_PW_POWERSHELL_COMMAND = f"""
$newPassword = Get-Content "{PATH_TO_PW_FILE}"
echo $newPassword | anydesk --set-password;
Start-Sleep -Seconds 1;
$serviceName="AnyDesk";
if((Get-Service -Name $serviceName).Status -eq "Running")
{{Restart-Service -Name $serviceName;}};
echo "Success"
"""
