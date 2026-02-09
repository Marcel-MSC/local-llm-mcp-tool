# Guia Rápido - Servidor MCP Llama

## Passo a Passo Rápido

### 1. Instalação Inicial

**Opção A: Script Automático (Mais Fácil)**

No PowerShell:
```powershell
.\install_llama.ps1
```

No CMD:
```cmd
install_llama.bat
```

**Opção B: Manual**

```bash
# 1. Instalar dependências básicas
pip install -r requirements.txt

# 2. Instalar llama-cpp-python (Windows - USE WHEELS PRÉ-COMPILADOS!)
# ⚠️ COPIE O COMANDO COMPLETO - não esqueça o --extra-index-url!

# CPU (recomendado para começar):
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# OU GPU NVIDIA (melhor performance):
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

**⚠️ IMPORTANTE:** 
- NÃO execute apenas `pip install llama-cpp-python` sem o `--extra-index-url`
- Isso causará erro de compilação!
- Veja `COMANDO_INSTALACAO.txt` para o comando exato

### 2. Configurar Modelo

```bash
# Copiar arquivo de exemplo
copy .env.example .env

# Baixar um modelo (recomendado)
python download_model.py

# OU editar .env manualmente e colocar o caminho do modelo
```

### 3. Testar

```bash
# Verificar se tudo está funcionando
python test_server.py
```

### 4. Executar Servidor

```bash
# Iniciar o servidor MCP
python server.py
```

### 5. Configurar no Cursor

1. Abra Cursor Settings (Ctrl+,)
2. Procure por "MCP Servers" ou edite manualmente
3. Adicione:

```json
{
  "mcpServers": {
    "local-llm": {
      "command": "python",
      "args": [
        "C:\\path\\to\\local-llm-mcp-tool\\server.py"
      ]
    }
  }
}
```

**⚠️ IMPORTANTE**: Substitua o caminho acima pelo caminho completo do seu `server.py`

4. Reinicie o Cursor
5. Pronto! O servidor deve aparecer na lista de MCP servers

## Comandos Úteis

- `python test_server.py` - Testa a configuração
- `python download_model.py` - Baixa modelos GGUF
- `python example_usage.py` - Exemplos de uso programático
- `python server.py` - Inicia o servidor MCP

## Modelos Recomendados

Para CPU (mais leve):
- Llama 3.2 1B - ~700MB
- Llama 3.2 3B - ~2GB

Para GPU ou CPU potente:
- Llama 3.1 8B - ~5GB
- Mistral 7B - ~4GB

## Solução de Problemas

**Erro ao carregar modelo?**
- Verifique se o caminho no `.env` está correto
- Use caminhos absolutos no Windows
- Certifique-se que o arquivo `.gguf` existe

**Servidor não aparece no Cursor?**
- Verifique o caminho na configuração (deve ser absoluto)
- Reinicie o Cursor
- Veja os logs do Cursor para erros

**Performance lenta?**
- Use modelos menores (1B-3B)
- Configure `N_GPU_LAYERS` no `.env` se tiver GPU
- Ajuste `N_THREADS` para número de cores da CPU
