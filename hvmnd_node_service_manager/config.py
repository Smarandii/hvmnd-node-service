import pathlib

PATH_TO_ANY_DESK = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe")
PATH_TO_PW_FILE = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\file.txt")
PATH_TO_LOG_FILE = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\logs.log")
HVMND_API_CLIENT_BASE_URL = "http://95.217.142.240:9876/api/v1"
RESTARTING_DISABLED = False
HVMND_API_TOKEN = "67509949-e9b4-800f-a556-eb61cbff2d81"
ALERT_BOT_TOKEN = "7309039400:AAGIvZDu4w6Zq4afAGOtkHlmf9tmfFvSYek"
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
