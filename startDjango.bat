@echo off
setlocal
set /p name="Enter the project name: "
set /p ipServ="Enter ip address with port (example: 1.2.3.4:8000): "
SET VENV_NAME=envWebDjango
SET VENV_PATH=%USERPROFILE%\%VENV_NAME%
SET MANAGE_PY=manage.py
SET PROJECT_NAME=%name%
SET WITH_IP= %ipServ%
SET ADD_DIR=

cd %USERPROFILE%\%PROJECT_NAME%

REM --- 1. Проверка наличия файла manage.py ---
if not exist "%MANAGE_PY%" (
    echo Error: The %MANAGE_PY% file was not found in the current directory.
    echo Make sure that you run the script from the root of your Django project.
    pause
    exit /b 1
)

REM --- 2. Проверка наличия виртуального окружения ---
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Error: The virtual environment "%VENV_NAME%" was not found on the path. "%VENV_PATH%".
    echo Please run setup_venv.bat first.
    pause
    exit /b 1
)

REM --- 3. Активация виртуального окружения ---
echo Activating the virtual environment %VENV_NAME%...
CALL "%VENV_PATH%\Scripts\activate.bat"

if %errorlevel% neq 0 (
    echo Error when activating the environment.
    pause
    exit /b 1
)

echo The environment is activated.

REM --- 4. Запуск сервера Django ---
echo Launching the Django server...
REM Эта команда использует python из активированного виртуального окружения
python manage.py runserver %WITH_IP%

REM Сервер будет работать до тех пор, пока вы не закроете консоль или не нажмете Ctrl+C

endlocal