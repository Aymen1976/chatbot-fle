@echo off
cd /d "C:\chemin\vers\ton\projet\fle-frontend"
start cmd /k "npm start"

cd /d "C:\chemin\vers\ton\projet\fle-backend"
start cmd /k "uvicorn main:app --reload"
