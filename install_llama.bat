@echo off
REM Batch script to install llama-cpp-python on Windows
REM This script installs using pre-built wheels

echo === llama-cpp-python Installer for Windows ===
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Remove previous installation if exists
echo Removing previous installations (if any)...
pip uninstall -y llama-cpp-python >nul 2>&1

echo.
echo Installing llama-cpp-python (CPU version)...
echo Using pre-built wheels to avoid compilation errors.
echo.

pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

if errorlevel 1 (
    echo.
    echo === Installation ERROR ===
    echo.
    echo Trying specific version...
    pip install llama-cpp-python==0.2.20 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
)

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    echo See docs/WINDOWS_INSTALLATION.md for more details
    pause
    exit /b 1
)

echo.
echo === Installation completed! ===
echo.
echo Testing installation...
python -c "from llama_cpp import Llama; print('OK: llama-cpp-python installed correctly!')"

if errorlevel 1 (
    echo Warning: Installation may have issues. Try testing manually.
) else (
    echo.
    echo All ready! You can continue with the MCP server configuration.
)

pause
