@echo off
setlocal

:: Define log file
set LOGFILE=update_node.log

:: Make admin the owner
takeown /F "%APPDATA%\render_hive_farm_bot_node_service" /A /R
icacls "%APPDATA%\render_hive_farm_bot_node_service" /inheritance:r /grant:r *S-1-5-32-544:(F) *S-1-5-18:(F) /remove:d *S-1-1-0 /T

:: Start logging
echo Updating service... > "%LOGFILE%"

echo Stopping render-node-service... >> "%LOGFILE%"

:: Stop the service
sc stop render-node-service >> "%LOGFILE%" 2>&1
timeout /t 5 >nul
sc query render-node-service | findstr /i "STOPPED" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo "Service did not stop successfully!" >> "%LOGFILE%"
    exit /b 1
)

echo Service stopped successfully. >> "%LOGFILE%"

:: Pull latest code
echo Pulling latest code... >> "%LOGFILE%"
git remote add origin-update "https://Smarandii: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@github.com/Smarandii/hvmnd-node-service.git" >> "%LOGFILE%" 2>&1
git pull origin-update master >> "%LOGFILE%" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo Git pull failed! >> "%LOGFILE%"
    exit /b 1
)

:: Run Python script directly
echo Running service setup... >> "%LOGFILE%"
.\venv\Scripts\python.exe render_node_setup.py >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Service setup failed! >> "%LOGFILE%"
    exit /b 1
)

:: Finish logging
echo Script completed successfully. >> "%LOGFILE%"
endlocal
exit /b 0
