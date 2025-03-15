@echo off
setlocal

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3 from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%release.py"

REM Check if the Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo Error: Python script not found at %PYTHON_SCRIPT%
    pause
    exit /b 1
)

REM Run the Python script with all arguments
python "%PYTHON_SCRIPT%" %*
if %ERRORLEVEL% neq 0 (
    echo Error: The Python script returned an error.
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0