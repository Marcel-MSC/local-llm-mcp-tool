# Local LLM MCP Tool

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)

A local MCP (Model Context Protocol) server that runs Llama models entirely on your machine. No API keys, no cloud costs, 100% private and offline-capable.

## ✨ Features

- 🚀 **100% Local** - All inference runs on your CPU/GPU, no data leaves your machine
- 🔒 **Private** - Your conversations stay on your device
- 💰 **Free** - No API costs or usage limits
- 🛠️ **Multiple Tools** - `generate_text`, `chat`, `complete`, `read_file`, `analyze_file`, and session management via MCP
- 💬 **Conversation History & Sessions** - Persistent session management with automatic history trimming to minimize storage
- 📡 **Streaming Support** - Optional incremental token streaming for faster response display
- 🪟 **Windows Optimized** - Pre-built wheels and installation scripts included
- 🔌 **Cursor Compatible** - Works seamlessly with Cursor IDE

### 🆕 Recent Additions

- **Conversation History & Sessions**: Create persistent conversation sessions with automatic history management. Sessions store messages in `history/` folder with configurable limits to minimize storage usage.
- **Streaming Responses**: Enable incremental token streaming for faster perceived response times. Configure chunk size and enable/disable via environment variables.

## 📋 Requirements

- Python 3.10 or higher
- Windows 10/11 (Linux/Mac support coming soon)
- A Llama model in GGUF format (can be downloaded automatically)

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Marcel-MSC/local-llm-mcp-tool.git
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

> ⚠️ **Note:** If you get compilation errors, see [WINDOWS_INSTALLATION.md](docs/WINDOWS_INSTALLATION.md) for troubleshooting. You can also install Visual Studio Build Tools to compile from source.

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
| `SESSION_HISTORY_DIR` | Directory for storing conversation history | `history` |
| `SESSION_MAX_MESSAGES` | Maximum messages per session (older messages trimmed) | `40` |
| `SESSION_MAX_FILE_BYTES` | Maximum size per session file (bytes) | `2097152` (~2MB) |
| `SESSION_AUTO_TRIM` | Automatically trim history when limits exceeded | `true` |
| `STREAMING_ENABLED` | Enable streaming responses (tokens sent incrementally) | `false` |
| `STREAMING_CHUNK_SIZE` | Approximate chunk size for streaming (characters) | `50` |

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

The server exposes several MCP tools:

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

### 4. `read_file`

Read a local text file from the MCP server's project directory. Relative paths are resolved from the directory containing `server.py`. Access is restricted to that directory tree (no `../..` traversal).

**Parameters:**
- `path` (required): File path (relative to the server root directory)
- `max_bytes` (optional, default: 200000): Maximum bytes to read (prevents huge reads)
- `encoding` (optional, default: `"utf-8"`): Text encoding used to decode file bytes

### 5. `analyze_file`

Read a local text file and ask the local Llama model to analyze it (purpose, structure, issues, improvements).

**Parameters:**
- `path` (required): File path (relative to the server root directory)
- `instruction` (optional): Custom analysis instruction (e.g. "Focus on security", "Summarize in 3 bullets")
- `max_bytes` (optional, default: 200000): Maximum bytes to read from the file
- `encoding` (optional, default: `"utf-8"`): File encoding
- `max_tokens` (optional, default: 512): Max tokens for the analysis response
- `temperature` (optional, default: 0.3): Sampling temperature for analysis

### 6. `start_session`

Start a new conversation session and get back a `session_id`. This groups
multiple turns together while keeping CPU and disk usage bounded.

**Parameters:**
- `metadata` (optional): JSON object with metadata like `purpose`, `label`, etc.

### 7. `continue_session`

Continue an existing session by adding a new user message. The server loads
only the most recent messages for context (limited by environment variables)
to avoid heavy CPU and storage usage.

**Parameters:**
- `session_id` (required): The ID returned by `start_session`.
- `message` (required): The new user message.
- `max_tokens` (optional, default: 256): Maximum tokens to generate.
- `temperature` (optional, default: 0.7): Sampling temperature.
- `top_p` (optional, default: 0.9): Top-p sampling.

### 8. `end_session`

Mark a session as ended and optionally delete its history from disk.

**Parameters:**
- `session_id` (required): The ID of the session to end.
- `delete` (optional, default: `false`): Whether to delete the stored history.

## 📚 Usage Examples

### In Cursor Chat

**Basic text generation:**
```
Use the generate_text tool from local-llm with prompt: Write a short sentence about programming.
```

**Chat with messages:**
```
Use the chat tool from local-llm with messages: [{"role": "user", "content": "What is Python?"}]
```

**Read a file from disk (returns the file text):**
```
Use the read_file tool from local-llm with:
path: README.md
```

**Analyze a file from disk (server reads the file and the LLM analyzes it):**
```
Use the analyze_file tool from local-llm with:
path: server.py
instruction: Summarize the main components and list 3 improvements.
```

**“Use generate_text and read README.md + server.py” (2-step workflow):**

1. Read each file (one tool call per file):
```
Use the read_file tool from local-llm with:
path: README.md
```
```
Use the read_file tool from local-llm with:
path: server.py
max_bytes: 200000
```

2. Then call `generate_text` using the file contents shown above in chat context:
```
Use the generate_text tool from local-llm with prompt: Compare the README and server.py content above. Are the documented tools accurate? List any mismatches and propose README fixes.
```

**Using conversation sessions:**

1. Start a session:
```
Use the start_session tool from local-llm with metadata: {"label": "coding-help"}
```

2. Continue the conversation (use the session_id from step 1):
```
Use the continue_session tool from local-llm with:
session_id: abc123...
message: How do I create a Python function?
```

3. Continue with more messages using the same session_id to maintain context.

4. End the session when done:
```
Use the end_session tool from local-llm with:
session_id: abc123...
delete: false
```

### Programmatic Usage

See `example_usage.py` for Python examples.

## 🎯 Recommended Models

Any Llama-compatible model in GGUF format works. Recommended:

- **Llama 3.2 1B** - Lightweight, fast, good for CPU
- **Llama 3.1 8B** - Balanced performance/quality
- **Mistral 7B** - Alternative option

Download from: [Hugging Face GGUF Models](https://huggingface.co/models?library=gguf)

## 💬 Conversation History & Sessions

The server supports **persistent conversation sessions** that maintain context across multiple interactions while minimizing storage and CPU usage.

### How Sessions Work

1. **Start a session** using `start_session` to get a unique `session_id`
2. **Continue conversations** using `continue_session` with the same `session_id` to maintain context
3. **History is stored** in the `history/` folder (one `.jsonl` file per session)
4. **Automatic trimming** keeps only the most recent messages (configurable limits)
5. **End sessions** with `end_session` when done (optionally delete history)

### Storage Management

- History files are stored in `history/<session_id>.jsonl` (line-delimited JSON)
- Session metadata is tracked in `history/sessions_index.json`
- Automatic trimming prevents unbounded growth:
  - Maximum messages per session (default: 40)
  - Maximum file size per session (default: ~2MB)
- The `history/` folder is gitignored by default

### Configuration

See the **Environment Variables** table above for session-related settings:
- `SESSION_HISTORY_DIR`: Where to store history files
- `SESSION_MAX_MESSAGES`: How many messages to keep per session
- `SESSION_MAX_FILE_BYTES`: Maximum file size before trimming
- `SESSION_AUTO_TRIM`: Enable/disable automatic trimming

### Example Session Flow

```python
# 1. Start session
session_id = start_session(metadata={"label": "coding-help"})

# 2. Continue conversation (maintains context)
response1 = continue_session(session_id, "What is Python?")
response2 = continue_session(session_id, "How do I create a function?")  # Remembers previous context

# 3. End session
end_session(session_id, delete=False)  # Keep history, or delete=True to remove
```

## 📡 Streaming Responses

The server supports **optional streaming** for faster response display. When enabled, tokens are sent incrementally as they're generated, rather than waiting for the complete response.

### Enabling Streaming

Set `STREAMING_ENABLED=true` in your `.env` file:

```env
STREAMING_ENABLED=true
STREAMING_CHUNK_SIZE=50
```

- **`STREAMING_ENABLED`**: Enable/disable streaming (default: `false`)
- **`STREAMING_CHUNK_SIZE`**: Approximate characters per chunk (default: `50`). Smaller values = more frequent updates but slightly more overhead.

### How It Works

When streaming is enabled:
- **`generate_text`**, **`chat`**, **`complete`**, and **`continue_session`** tools return multiple `TextContent` chunks
- Each chunk contains a portion of the generated text
- The client (Cursor) can display text incrementally as it arrives
- For **`continue_session`**, the full accumulated text is still persisted to session history after streaming completes

### Performance Notes

- Streaming adds minimal CPU overhead (just chunking logic)
- Response **quality** is unchanged - streaming only affects **delivery timing**
- On slower machines, consider using smaller models (1B-3B) with streaming enabled for best experience
- Streaming works with both CPU and GPU inference

### Disabling Streaming

Set `STREAMING_ENABLED=false` (or omit it) to return complete responses in a single chunk, matching the original behavior.

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
- See [INSTALL_COMPILER_WINDOWS.md](docs/INSTALL_COMPILER_WINDOWS.md) for installing Visual Studio Build Tools
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

See [FUTURE_IDEAS.md](docs/FUTURE_IDEAS.md) for planned features:
- ✅ ~~Conversation history/sessions~~ - **Implemented!**
- ✅ ~~Streaming responses~~ - **Implemented!**
- RAG (document Q&A)
- Multiple model support
- Session summarization for long conversations
- And more...

---

**Made with ❤️ for privacy-conscious developers who want local AI without the cloud.**
