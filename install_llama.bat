@echo off
REM Script batch para instalar llama-cpp-python no Windows
REM Este script instala usando wheels pré-compilados

echo === Instalador llama-cpp-python para Windows ===
echo.

REM Verifica Python
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.10 ou superior de https://www.python.org/
    pause
    exit /b 1
)

REM Remove instalação anterior se existir
echo Removendo instalacoes anteriores (se houver)...
pip uninstall -y llama-cpp-python >nul 2>&1

echo.
echo Instalando llama-cpp-python (versao CPU)...
echo Usando wheels pre-compilados para evitar erros de compilacao.
echo.

pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

if errorlevel 1 (
    echo.
    echo === ERRO na instalacao ===
    echo.
    echo Tentando versao especifica...
    pip install llama-cpp-python==0.2.20 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
)

if errorlevel 1 (
    echo.
    echo ERRO: Falha na instalacao
    echo Consulte INSTALACAO_WINDOWS.md para mais detalhes
    pause
    exit /b 1
)

echo.
echo === Instalacao concluida! ===
echo.
echo Testando instalacao...
python -c "from llama_cpp import Llama; print('OK: llama-cpp-python instalado corretamente!')"

if errorlevel 1 (
    echo Aviso: A instalacao pode ter problemas. Tente testar manualmente.
) else (
    echo.
    echo Tudo pronto! Voce pode continuar com a configuracao do servidor MCP.
)

pause
