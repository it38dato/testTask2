@echo off
setlocal
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python was not found. First, install Python and add it to the PATH.
    pause
    exit /b 1
)
set /p name="Enter the project name: "
SET VENV_NAME=envWebDjango
SET VENV_PATH=%USERPROFILE%\%VENV_NAME%
SET REQS_FILE=requirements.txt
SET PROJECT_NAME=%name%
SET APP_NAME=webApp
echo Home Directory: %USERPROFILE%
echo The path to the virtual environment: %VENV_PATH%
echo Requirements file: %REQS_FILE%
if not exist "%VENV_PATH%" (
    echo Creating a virtual environment "%VENV_NAME%"...
    python -m venv "%VENV_PATH%"
    if %errorlevel% neq 0 (
        echo Error when creating a virtual environment.
        pause
        exit /b 1
    )
    echo The virtual environment has been successfully created.
) else (
    echo The virtual environment "%VENV_NAME%" already exists. Skipping the creation.
)
echo Activating the virtual environment and installing libraries from %REQS_FILE%...
CALL "%VENV_PATH%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Error when activating the environment.
    pause
    exit /b 1
)
pip install --upgrade pip --proxy http://YOURPROXY:8080
pip install -r "%REQS_FILE%" --proxy http://YOURPROXY:8080
if %errorlevel% neq 0 (
    echo Error when installing libraries.
    pause
    exit /b 1
)
echo Everything is ready! The %VENV_NAME% virtual environment is configured.
echo Libraries from %REQS_FILE% are installed:
pip list
echo To activate the environment manually later, use the command (bat or ps1):
echo CALL "%VENV_PATH%\Scripts\activate.bat"
echo OR
echo CALL "%VENV_PATH%\Scripts\activate.ps1"

::xcopy /s config.txt %USERPROFILE%\%PROJECT_NAME%

cd %USERPROFILE%
echo Checking for Django availability...
where django-admin >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: django-admin was not found. Make sure that Django was installed via requirements.txt
    pause
    exit /b 1
)
echo Creating a Django project "%PROJECT_NAME%" in the current directory...
django-admin startproject %PROJECT_NAME%
if %errorlevel% neq 0 (
    echo Error when creating a Django project.
    pause
    exit /b 1
)
echo The Django project "%PROJECT_NAME%" has been successfully created in:
echo %USERPROFILE%\%PROJECT_NAME%

echo Launching the Django server...
cd %USERPROFILE%\%PROJECT_NAME%
python manage.py startapp %APP_NAME%
python manage.py migrate
python manage.py createsuperuser

pause
endlocal