# Local LLM MCP Tool

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)

A local MCP (Model Context Protocol) server that runs Llama models entirely on your machine. No API keys, no cloud costs, 100% private and offline-capable.

## ✨ Features

- 🚀 **100% Local** - All inference runs on your CPU/GPU, no data leaves your machine
- 🔒 **Private** - Your conversations stay on your device
- 💰 **Free** - No API costs or usage limits
- 🛠️ **Three Tools** - `generate_text`, `chat`, and `complete` via MCP
- 🪟 **Windows Optimized** - Pre-built wheels and installation scripts included
- 🔌 **Cursor Compatible** - Works seamlessly with Cursor IDE

## 📋 Requirements

- Python 3.10 or higher
- Windows 10/11 (Linux/Mac support coming soon)
- A Llama model in GGUF format (can be downloaded automatically)

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/local-llm-mcp-tool.git
cd local-llm-mcp-tool
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install llama-cpp-python

**For Windows, use pre-built wheels (recommended):**

**Option A: CPU only**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

**Option B: NVIDIA GPU (better performance)**
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

**Or use the automated installer:**

**PowerShell:**
```powershell
.\install_llama.ps1
```

**CMD/Batch:**
```cmd
install_llama.bat
```

> ⚠️ **Note:** If you get compilation errors, see [INSTALACAO_WINDOWS.md](INSTALACAO_WINDOWS.md) for troubleshooting. You can also install Visual Studio Build Tools to compile from source.

### 4. Configure the model

```bash
copy .env.example .env
```

Edit `.env` and set your model path:

```env
MODEL_PATH=C:\path\to\your\model.gguf
```

### 5. Download a model (if needed)

```bash
python download_model.py
```

Or download manually from [Hugging Face](https://huggingface.co/models?library=gguf) and update `MODEL_PATH` in `.env`.

### 6. Test the setup

```bash
python test_server.py
```

### 7. Run the server

```bash
python server.py
```

Or use the FastMCP version (simpler):

```bash
python server_fastmcp.py
```

## 🔧 Configuration

### Environment Variables (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_PATH` | Path to your GGUF model file | Required |
| `CONTEXT_SIZE` | Maximum context window size | `2048` |
| `N_THREADS` | Number of CPU threads | `4` |
| `N_GPU_LAYERS` | GPU layers (use `-1` for all, `0` for CPU only) | `0` |

### Using with Cursor IDE

1. Open Cursor Settings (`Ctrl+,`)
2. Search for "MCP" or edit `settings.json` directly
3. Add the configuration:

```json
{
  "mcpServers": {
    "local-llm": {
      "command": "python",
      "args": [
        "C:\\path\\to\\local-llm-mcp-tool\\server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Or use project-specific config:** Create `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "local-llm": {
      "command": "python",
      "args": [
        "C:\\path\\to\\local-llm-mcp-tool\\server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

4. Restart Cursor
5. The server will appear in **Tools & MCP** → **Installed MCP Servers**

## 🛠️ Available Tools

The server exposes three MCP tools:

### 1. `generate_text`

Generate text using the local Llama model.

**Parameters:**
- `prompt` (required): The text prompt
- `max_tokens` (optional, default: 256): Maximum tokens to generate
- `temperature` (optional, default: 0.7): Sampling temperature (0.0-2.0)
- `top_p` (optional, default: 0.9): Top-p sampling (0.0-1.0)

### 2. `chat`

Chat with the model using a message-based format.

**Parameters:**
- `messages` (required): Array of messages `[{"role": "user", "content": "..."}]`
- `max_tokens` (optional, default: 256): Maximum tokens to generate
- `temperature` (optional, default: 0.7): Sampling temperature

### 3. `complete`

Complete a text prompt.

**Parameters:**
- `text` (required): The text to complete
- `max_tokens` (optional, default: 128): Maximum tokens to generate
- `temperature` (optional, default: 0.7): Sampling temperature

## 📚 Usage Examples

### In Cursor Chat

Ask the AI to use the tools:

```
Use the generate_text tool from local-llm with prompt: Write a short sentence about programming.
```

```
Use the chat tool from local-llm with message: What is Python?
```

### Programmatic Usage

See `example_usage.py` for Python examples.

## 🎯 Recommended Models

Any Llama-compatible model in GGUF format works. Recommended:

- **Llama 3.2 1B** - Lightweight, fast, good for CPU
- **Llama 3.1 8B** - Balanced performance/quality
- **Mistral 7B** - Alternative option

Download from: [Hugging Face GGUF Models](https://huggingface.co/models?library=gguf)

## 🐛 Troubleshooting

### Error: "Model not found"
- Verify `MODEL_PATH` in `.env` is correct
- Use absolute paths on Windows
- Ensure the `.gguf` file exists

### Error: "llama-cpp-python not installed"
- Install with: `pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`
- For GPU: `pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121`

### Server doesn't appear in Cursor
- Check the path in your MCP configuration
- Use absolute paths with double backslashes (`\\`) or forward slashes
- Restart Cursor after adding configuration
- Check Cursor's Output panel (MCP logs) for errors

### Slow performance
- Use smaller models (1B-3B) for CPU-only setups
- Set `N_GPU_LAYERS=-1` in `.env` if you have NVIDIA GPU
- Adjust `N_THREADS` to match your CPU cores
- Reduce `CONTEXT_SIZE` if you don't need long context

### Compilation errors on Windows
- See [INSTALAR_COMPILADOR_WINDOWS.md](INSTALAR_COMPILADOR_WINDOWS.md) for installing Visual Studio Build Tools
- Or use pre-built wheels (recommended)

## 📁 Project Structure

```
local-llm-mcp-tool/
├── server.py              # Main MCP server (standard API)
├── server_fastmcp.py      # Alternative server (FastMCP, simpler)
├── example_usage.py       # Usage examples
├── download_model.py      # Model download helper
├── test_server.py         # Setup test script
├── install_llama.ps1       # PowerShell installer
├── install_llama.bat      # Batch installer
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - The core inference engine
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) - Python bindings
- [Model Context Protocol](https://modelcontextprotocol.io/) - The MCP specification
- [Cursor](https://cursor.sh/) - The IDE that makes this useful

## 🔮 Future Ideas

See [IDEAS_EVOLUCAO.md](IDEAS_EVOLUCAO.md) for planned features:
- Conversation history/sessions
- Streaming responses
- RAG (document Q&A)
- Multiple model support
- And more...

---

**Made with ❤️ for privacy-conscious developers who want local AI without the cloud.**
