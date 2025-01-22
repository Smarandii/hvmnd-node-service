@echo off
setlocal

powershell -ExecutionPolicy Bypass -Command "git pull origin master"
powershell -ExecutionPolicy Bypass -Command "..\ .\venv\Scripts\activate; python ..\render_node_setup.py"

echo Script completed successfully.
endlocal
exit /b 0
