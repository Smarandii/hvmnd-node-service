import pathlib

PATH_TO_ANY_DESK = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe")
PATH_TO_PW_FILE = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\file.txt")
PATH_TO_LOG_FILE = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\logs.log")
PG_URL = "postgresql://u392hn6janvdjd:p63b381c7fe01cb1f1e89cf0549dd4a6fb8be076c9af3d03b71e29692ee94624d@c7vbm80blivm58.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d40tce2ulgaggj"
MONGO_URI = "mongodb+srv://admin:WIyniFnVBpcbG1pJ@cluster0.aaaafpm.mongodb.net/?retryWrites=true&w=majority"
ALERT_BOT_TOKEN = "6524183208:AAHXOGhNtuQ1mHis-3J9_tsd01ZI0CTIX60"
FRONTEND_BOT_TOKEN = "6164392242:AAFGGTh63f3tnhjj8fwqcxRwS_Rh67UeU1I"
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