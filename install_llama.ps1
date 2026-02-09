# Script PowerShell para instalar llama-cpp-python no Windows
# Este script instala usando wheels pré-compilados

Write-Host "=== Instalador llama-cpp-python para Windows ===" -ForegroundColor Cyan
Write-Host ""

# Verifica versão do Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale Python 3.10 ou superior de https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green

# Verifica pip
Write-Host "Verificando pip..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: pip não encontrado!" -ForegroundColor Red
    exit 1
}
Write-Host "pip encontrado: $pipVersion" -ForegroundColor Green
Write-Host ""

# Pergunta qual versão instalar
Write-Host "Qual versão você quer instalar?" -ForegroundColor Cyan
Write-Host "1. CPU (recomendado para começar)"
Write-Host "2. GPU NVIDIA (CUDA 12.1)"
Write-Host "3. GPU NVIDIA (CUDA 11.8)"
Write-Host ""
$choice = Read-Host "Escolha (1-3)"

$indexUrl = ""
switch ($choice) {
    "1" {
        $indexUrl = "https://abetlen.github.io/llama-cpp-python/whl/cpu"
        Write-Host "Instalando versão CPU..." -ForegroundColor Yellow
    }
    "2" {
        $indexUrl = "https://abetlen.github.io/llama-cpp-python/whl/cu121"
        Write-Host "Instalando versão GPU (CUDA 12.1)..." -ForegroundColor Yellow
    }
    "3" {
        $indexUrl = "https://abetlen.github.io/llama-cpp-python/whl/cu118"
        Write-Host "Instalando versão GPU (CUDA 11.8)..." -ForegroundColor Yellow
    }
    default {
        Write-Host "Opção inválida. Usando CPU por padrão." -ForegroundColor Yellow
        $indexUrl = "https://abetlen.github.io/llama-cpp-python/whl/cpu"
    }
}

Write-Host ""
Write-Host "Executando: pip install llama-cpp-python --extra-index-url $indexUrl" -ForegroundColor Gray
Write-Host ""

# Tenta desinstalar versão anterior se existir
Write-Host "Removendo instalações anteriores (se houver)..." -ForegroundColor Yellow
pip uninstall -y llama-cpp-python 2>$null

# Instala usando wheels pré-compilados
Write-Host "Instalando llama-cpp-python..." -ForegroundColor Yellow
pip install llama-cpp-python --extra-index-url $indexUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Instalação concluída com sucesso! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Testando instalação..." -ForegroundColor Yellow
    python -c "from llama_cpp import Llama; print('✓ llama-cpp-python instalado corretamente!')"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Tudo pronto! Você pode continuar com a configuração do servidor MCP." -ForegroundColor Green
    } else {
        Write-Host "Aviso: A instalação pode ter problemas. Tente testar manualmente." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "=== ERRO na instalação ===" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis soluções:" -ForegroundColor Yellow
    Write-Host "1. Verifique sua conexão com a internet"
    Write-Host "2. Tente uma versão específica:"
    Write-Host "   pip install llama-cpp-python==0.2.20 --extra-index-url $indexUrl"
    Write-Host "3. Verifique se sua versão do Python é 3.10 ou superior"
    Write-Host "4. Consulte INSTALACAO_WINDOWS.md para mais detalhes"
}
