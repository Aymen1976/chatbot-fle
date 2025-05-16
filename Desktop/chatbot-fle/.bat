@echo off
echo Lancement du backend...
start cmd /k "cd fle-backend && uvicorn main:app --reload"

timeout /t 2 >nul

echo Lancement du frontend...
start cmd /k "cd frontend-app && npm start"
