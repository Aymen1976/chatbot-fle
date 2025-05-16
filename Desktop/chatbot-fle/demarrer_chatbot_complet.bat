@echo off
start cmd /k "cd /d fle-backend && uvicorn main:app --reload"
start cmd /k "cd /d frontend-app && npm start"
