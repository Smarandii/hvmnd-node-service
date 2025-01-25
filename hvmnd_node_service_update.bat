@echo off
setlocal

:: Define log file
set LOGFILE=update_node.log

echo Running under user: %USERNAME% >> "%LOGFILE%"
whoami >> "%LOGFILE%"

:: Start a new detached process for the actual script
start "" cmd.exe /c "hvmnd_node_service_update_worker.bat"
exit /b
