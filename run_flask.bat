@echo off
call .venv\Scripts\activate
start cmd /k "flask --app app.py run"
timeout /t 2 >nul
start http://127.0.0.1:5000/