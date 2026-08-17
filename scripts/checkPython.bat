@echo off
setlocal
echo Checking for Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is NOT installed or added to the PATH.
    echo Please install Python from the official website.: https://www.python.org/downloads/
    echo MAKE SURE to check the box "Add Python to PATH" during installation.
    pause
    goto :eof
)
for /f "tokens=*" %%v in ('python -V 2^>^&1') do set "python_version=%%v"
echo Python has been successfully found. Version: %python_version%
endlocal
pause
goto :eof
