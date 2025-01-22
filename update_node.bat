@echo off
setlocal

powershell git pull origin master
powershell .\venv\Scripts\activate
powershell python render_node_setup.py

echo Script completed successfully.
endlocal
exit /b 0
