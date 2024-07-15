import pathlib

PATH_TO_ANY_DESK = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe")
PATH_TO_PW_FILE = pathlib.Path(r"C:\Program Files (x86)\AnyDesk\file.txt")
# PATH_TO_ANY_DESK = pathlib.Path(r"E:\ProgramFiles(x86)\AnyDesk\AnyDesk.exe")
# PATH_TO_PW_FILE = pathlib.Path(r"E:\ProgramFiles(x86)\AnyDesk\file.txt")
PG_URL = "postgresql://u392hn6janvdjd:p8559ad6981e53b1d57a187b23299ae67e5523326c22c28d950c1195c8cfa1a25@cav8p52l9arddb.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d244tq42h7f2ig"
MONGO_URI = "mongodb+srv://admin:WIyniFnVBpcbG1pJ@cluster0.aaaafpm.mongodb.net/?retryWrites=true&w=majority"
token = "6524183208:AAHXOGhNtuQ1mHis-3J9_tsd01ZI0CTIX60"
bot_token = "6164392242:AAFGGTh63f3tnhjj8fwqcxRwS_Rh67UeU1I"
chat_id = "231584958"
UPDATE_PW_POWERSHELL_COMMAND = f"""
$newPassword = Get-Content "{PATH_TO_PW_FILE}"
echo $newPassword | anydesk --set-password;
Start-Sleep -Seconds 1;
$serviceName="AnyDesk";
if((Get-Service -Name $serviceName).Status -eq "Running")
{{Restart-Service -Name $serviceName;}};
echo "Success"
"""