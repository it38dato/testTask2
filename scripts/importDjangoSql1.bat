@echo off
setlocal
SET VENV_NAME=forTemplate\env
SET VENV_PATH=%USERPROFILE%\%VENV_NAME%
SET MANAGE_PY=manage.py
SET DJANGO_PROJECT_NAME=webTemplate
::SET DJANGO_PROJECT_NAME=main
SET WITH_IP= 
SET ADD_DIR=Documents\projects\webTemplate

cd %USERPROFILE%\%DJANGO_PROJECT_NAME%
::cd %USERPROFILE%\%ADD_DIR%\%DJANGO_PROJECT_NAME%
if not exist "%MANAGE_PY%" (
    echo Error: The %MANAGE_PY% file was not found in the current directory.
    echo Make sure that you run the script from the root of your Django project.
    pause
    exit /b 1
)
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Error: The virtual environment "%VENV_NAME%" was not found on the path. "%VENV_PATH%".
    echo Please run setup_venv.bat first.
    pause
    exit /b 1
)
echo Activating the virtual environment %VENV_NAME%...
CALL "%VENV_PATH%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Error when activating the environment.
    pause
    exit /b 1
)
echo The environment is activated.
echo Launching the Django server...
set PYTHONIOENCODING=utf8
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > datadump.json
set PYTHONIOENCODING=
endlocal
pause