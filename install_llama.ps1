# PowerShell script to install llama-cpp-python on Windows
# This script installs using pre-built wheels

Write-Host "=== llama-cpp-python Installer for Windows ===" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Install Python 3.10 or higher from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "Python found: $pythonVersion" -ForegroundColor Green

# Check pip
Write-Host "Checking pip..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip not found!" -ForegroundColor Red
    exit 1
}
Write-Host "pip found: $pipVersion" -ForegroundColor Green
Write-Host ""

# Ask which version to install
Write-Host "Which version do you want to install?" -ForegroundColor Cyan
Write-Host "1. CPU (recommended to start)"
Write-Host "2. NVIDIA GPU (CUDA 12.1)"
Write-Host "3. NVIDIA GPU (CUDA 11.8)"
Write-Host ""
$choice = Read-Host "Choose (1-3)"

$indexUrl = ""
switch ($choice) {
    "1" {
        $indexUrl = "https://abetlen.github.io/llama-cpp-python/whl/cpu"
        Write-Host "Installing CPU version..." -ForegroundColor Yellow
    }
    "2" {
        $indexUrl = "https://abetlen.github.io/llama-cpp-python/whl/cu121"
        Write-Host "Installing GPU version (CUDA 12.1)..." -ForegroundColor Yellow
    }
    "3" {
        $indexUrl = "https://abetlen.github.io/llama-cpp-python/whl/cu118"
        Write-Host "Installing GPU version (CUDA 11.8)..." -ForegroundColor Yellow
    }
    default {
        Write-Host "Invalid option. Using CPU by default." -ForegroundColor Yellow
        $indexUrl = "https://abetlen.github.io/llama-cpp-python/whl/cpu"
    }
}

Write-Host ""
Write-Host "Running: pip install llama-cpp-python --extra-index-url $indexUrl" -ForegroundColor Gray
Write-Host ""

# Try to uninstall previous version if exists
Write-Host "Removing previous installations (if any)..." -ForegroundColor Yellow
pip uninstall -y llama-cpp-python 2>$null

# Install using pre-built wheels
Write-Host "Installing llama-cpp-python..." -ForegroundColor Yellow
pip install llama-cpp-python --extra-index-url $indexUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Installation completed successfully! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Testing installation..." -ForegroundColor Yellow
    python -c "from llama_cpp import Llama; print('✓ llama-cpp-python installed correctly!')"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "All ready! You can continue with the MCP server configuration." -ForegroundColor Green
    } else {
        Write-Host "Warning: Installation may have issues. Try testing manually." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "=== Installation ERROR ===" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "1. Check your internet connection"
    Write-Host "2. Try a specific version:"
    Write-Host "   pip install llama-cpp-python==0.2.20 --extra-index-url $indexUrl"
    Write-Host "3. Check if your Python version is 3.10 or higher"
    Write-Host "4. See docs/WINDOWS_INSTALLATION.md for more details"
}
