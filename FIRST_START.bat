@echo off
echo ===============================
echo          FIRST SETUP 
echo ===============================

echo.
echo [1/6] Sprawdzam Pythona...
python --version || exit /b 1

echo.
echo [2/6] Tworze virtualenv...
python -m venv venv

echo.
echo [3/6] Aktywuje virtualenv...
call venv\Scripts\activate

echo.
echo [4/6] Aktualizuje pip...
python -m pip install --upgrade pip

echo.
echo [5/6] Instaluje Django...
pip install django

echo.
echo [6/6] Instaluje biblioteki...
pip install djangorestframework
pip install django-cors-headers


echo.
echo ===============================
echo GOTOWE
echo Aby uruchomic:
echo   Otworz plik start.bat
echo ===============================

pause
