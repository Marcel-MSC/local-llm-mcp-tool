# Quick Guide - Llama MCP Server

## Quick Step-by-Step

### 1. Initial Installation

**Option A: Automated Script (Easiest)**

In PowerShell:
```powershell
.\install_llama.ps1
```

In CMD:
```cmd
install_llama.bat
```

**Option B: Manual**

```bash
# 1. Install basic dependencies
pip install -r requirements.txt

# 2. Install llama-cpp-python (Windows - USE PRE-BUILT WHEELS!)
# ⚠️ COPY THE COMPLETE COMMAND - don't forget the --extra-index-url!

# CPU (recommended to start):
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# OR NVIDIA GPU (better performance):
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

**⚠️ IMPORTANT:** 
- Do NOT run just `pip install llama-cpp-python` without the `--extra-index-url`
- This will cause compilation errors!
- See the installation command examples above

### 2. Configure Model

```bash
# Copy example file
copy .env.example .env

# Download a model (recommended)
python download_model.py

# OR edit .env manually and set the model path
```

### 3. Test

```bash
# Verify everything is working
python test_server.py
```

### 4. Run Server

```bash
# Start the MCP server
python server.py
```

### 5. Configure in Cursor

1. Open Cursor Settings (Ctrl+,)
2. Search for "MCP Servers" or edit manually
3. Add:

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

**⚠️ IMPORTANT**: Replace the path above with the full path to your `server.py`

4. Restart Cursor
5. Done! The server should appear in the MCP servers list

## Useful Commands

- `python test_server.py` - Test the configuration
- `python download_model.py` - Download GGUF models
- `python example_usage.py` - Programmatic usage examples
- `python server.py` - Start the MCP server

## Recommended Models

For CPU (lighter):
- Llama 3.2 1B - ~700MB
- Llama 3.2 3B - ~2GB

For GPU or powerful CPU:
- Llama 3.1 8B - ~5GB
- Mistral 7B - ~4GB

## Troubleshooting

**Error loading model?**
- Check if the path in `.env` is correct
- Use absolute paths on Windows
- Make sure the `.gguf` file exists

**Server doesn't appear in Cursor?**
- Check the path in configuration (must be absolute)
- Restart Cursor
- Check Cursor logs for errors

**Slow performance?**
- Use smaller models (1B-3B)
- Configure `N_GPU_LAYERS` in `.env` if you have GPU
- Adjust `N_THREADS` to number of CPU cores
