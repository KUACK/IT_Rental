@echo off
REM Przechodzimy do folderu ze skryptem
cd /d %~dp0

REM Aktywujemy wirtualne środowisko
call venv\Scripts\activate.bat

REM Uruchamiamy serwer Django w nowym oknie
start cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python manage.py runserver"

REM Czekamy chwilę, żeby serwer zdążył wystartować
timeout /t 1 /nobreak >nul

REM Otwieramy przeglądarkę Edge w trybie InPrivate
start msedge.exe --inprivate http://127.0.0.1:8000/