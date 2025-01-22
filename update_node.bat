@echo off
setlocal

echo Updating service... > update_node.log

git remote add origin-update "https://Smarandii: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@github.com/Smarandii/hvmnd-node-service.git"
git pull origin-update master || echo Git pull failed! && exit /b 1

echo Activating virtual environment and updating service... > update_node.log
powershell -ExecutionPolicy Bypass -Command ". .\venv\Scripts\activate; python render_node_setup.py" || echo Service setup failed! > update_node.log && exit /b 1

echo Script completed successfully. > update_node.log
endlocal
exit /b 0