#!/usr/bin/env python3
"""
MCP server with Llama integration for local execution
"""
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

try:
    from llama_cpp import Llama
except ImportError:
    print("Error: llama-cpp-python is not installed.")
    print("Install with: pip install llama-cpp-python")
    sys.exit(1)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP library is not installed.")
    print("Install with: pip install mcp")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Default configurations
DEFAULT_MODEL_PATH = os.getenv("MODEL_PATH", "")
DEFAULT_CONTEXT_SIZE = int(os.getenv("CONTEXT_SIZE", "2048"))
DEFAULT_N_THREADS = int(os.getenv("N_THREADS", "4"))
DEFAULT_N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", "0"))

# Session / history configuration
DEFAULT_SESSION_HISTORY_DIR = os.getenv("SESSION_HISTORY_DIR", "history")
DEFAULT_SESSION_MAX_MESSAGES = int(os.getenv("SESSION_MAX_MESSAGES", "40"))
DEFAULT_SESSION_MAX_FILE_BYTES = int(os.getenv("SESSION_MAX_FILE_BYTES", str(2 * 1024 * 1024)))  # ~2MB
DEFAULT_SESSION_AUTO_TRIM = os.getenv("SESSION_AUTO_TRIM", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# Streaming configuration
DEFAULT_STREAMING_ENABLED = os.getenv("STREAMING_ENABLED", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
DEFAULT_STREAMING_CHUNK_SIZE = int(os.getenv("STREAMING_CHUNK_SIZE", "50"))

BASE_DIR = Path(__file__).resolve().parent
HISTORY_DIR = BASE_DIR / DEFAULT_SESSION_HISTORY_DIR
SESSIONS_INDEX_PATH = HISTORY_DIR / "sessions_index.json"

# Global model instance and current path
llama_model: Optional[Llama] = None
_current_model_path: Optional[str] = None

MODELS_DIR = os.getenv("MODELS_DIR", "")
if not MODELS_DIR:
    MODELS_DIR = str(BASE_DIR / "models")


def get_available_models() -> List[Dict[str, str]]:
    """List available GGUF models in MODELS_DIR and MODEL_PATH."""
    models = []
    seen = set()

    # Scan models directory
    models_path = Path(MODELS_DIR)
    if models_path.exists() and models_path.is_dir():
        for p in models_path.glob("*.gguf"):
            path_str = str(p.resolve())
            if path_str not in seen:
                seen.add(path_str)
                models.append({"path": path_str, "name": p.name})

    # Include DEFAULT_MODEL_PATH if set and not already listed
    if DEFAULT_MODEL_PATH and os.path.exists(DEFAULT_MODEL_PATH):
        path_str = str(Path(DEFAULT_MODEL_PATH).resolve())
        if path_str not in seen:
            seen.add(path_str)
            models.append({"path": path_str, "name": Path(DEFAULT_MODEL_PATH).name})

    return sorted(models, key=lambda x: x["name"].lower())


def unload_model() -> None:
    """Unload the current model to free memory."""
    global llama_model, _current_model_path
    if llama_model is not None:
        try:
            del llama_model
        except Exception:
            pass
        llama_model = None
        _current_model_path = None
        import gc
        gc.collect()
        print("Model unloaded.", file=sys.stderr)


def load_model(model_path: Optional[str] = None) -> Llama:
    """Loads the Llama model. Pass model_path to switch to a different model."""
    global llama_model, _current_model_path

    path = model_path or DEFAULT_MODEL_PATH
    if not path:
        path = DEFAULT_MODEL_PATH

    path_resolved = str(Path(path).resolve()) if path else ""

    # If requesting a different model, unload first
    if llama_model is not None and _current_model_path != path_resolved:
        unload_model()

    if llama_model is not None:
        return llama_model

    if not path or not os.path.exists(path):
        error_msg = (
            f"Error: Model not found at {path}\nPlease configure MODEL_PATH in the .env file\n"
            "Or download a GGUF model from: https://huggingface.co/models?library=gguf"
        )
        print(error_msg, file=sys.stderr)
        raise FileNotFoundError(f"Model not found: {path}")

    print(f"Loading model from: {path}", file=sys.stderr)

    try:
        llama_model = Llama(
            model_path=path,
            n_ctx=DEFAULT_CONTEXT_SIZE,
            n_threads=DEFAULT_N_THREADS,
            n_gpu_layers=DEFAULT_N_GPU_LAYERS,
            verbose=False,
        )
        _current_model_path = path_resolved
        print("Model loaded successfully!", file=sys.stderr)
        return llama_model
    except Exception as e:
        print(f"Error loading model: {e}", file=sys.stderr)
        raise


def get_current_model_path() -> Optional[str]:
    """Return the path of the currently loaded model."""
    return _current_model_path


# === Streaming generation helpers =============================================

def generate_with_streaming(
    model: Llama,
    prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop: Optional[List[str]] = None,
    chunk_size: int = DEFAULT_STREAMING_CHUNK_SIZE,
) -> List[TextContent]:
    """Generate text with streaming enabled, returning multiple TextContent chunks.
    
    Returns a list of TextContent objects, one per chunk, for incremental display.
    """
    stop_sequences = stop or []
    
    # Use stream=True to get incremental tokens
    stream = model(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        echo=False,
        stop=stop_sequences,
        stream=True,
    )
    
    chunks: List[TextContent] = []
    current_chunk = ""
    
    for chunk in stream:
        if "choices" in chunk and len(chunk["choices"]) > 0:
            delta_text = chunk["choices"][0].get("text", "")
            if delta_text:
                current_chunk += delta_text
                
                # Emit chunk when it reaches the target size
                if len(current_chunk) >= chunk_size:
                    chunks.append(TextContent(type="text", text=current_chunk))
                    current_chunk = ""
    
    # Emit any remaining text as final chunk
    if current_chunk:
        chunks.append(TextContent(type="text", text=current_chunk))
    
    # If no chunks were emitted (empty response), return at least one empty chunk
    if not chunks:
        chunks.append(TextContent(type="text", text=""))
    
    return chunks


def generate_without_streaming(
    model: Llama,
    prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop: Optional[List[str]] = None,
) -> List[TextContent]:
    """Generate text without streaming, returning a single TextContent with full response."""
    stop_sequences = stop or []
    
    output = model(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        echo=False,
        stop=stop_sequences,
    )
    
    generated_text = output["choices"][0]["text"]
    return [TextContent(type="text", text=generated_text)]


def generate_completion(
    model: Llama,
    prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop: Optional[List[str]] = None,
    streaming: bool = False,
    chunk_size: int = DEFAULT_STREAMING_CHUNK_SIZE,
) -> tuple[List[TextContent], str]:
    """Generate completion with optional streaming.
    
    Returns:
        - List of TextContent objects (multiple chunks if streaming, single chunk otherwise)
        - Full accumulated text (for session persistence)
    """
    if streaming:
        chunks = generate_with_streaming(
            model, prompt, max_tokens, temperature, top_p, stop, chunk_size
        )
        # Accumulate full text from chunks
        full_text = "".join(chunk.text for chunk in chunks)
        return chunks, full_text
    else:
        chunks = generate_without_streaming(
            model, prompt, max_tokens, temperature, top_p, stop
        )
        full_text = chunks[0].text if chunks else ""
        return chunks, full_text


# === Session storage helpers ==================================================

def _ensure_history_dir() -> None:
    """Ensure the history directory and index file exist."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    if not SESSIONS_INDEX_PATH.exists():
        initial_index = {"sessions": {}}
        SESSIONS_INDEX_PATH.write_text(
            json.dumps(initial_index, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _load_sessions_index() -> Dict[str, Any]:
    """Load the sessions index from disk."""
    _ensure_history_dir()
    try:
        raw = SESSIONS_INDEX_PATH.read_text(encoding="utf-8")
        if not raw.strip():
            return {"sessions": {}}
        data = json.loads(raw)
        if "sessions" not in data or not isinstance(data["sessions"], dict):
            return {"sessions": {}}
        return data
    except Exception:
        # Corrupt or unreadable index; start fresh but don't delete any history files
        return {"sessions": {}}


def _save_sessions_index(index: Dict[str, Any]) -> None:
    """Persist the sessions index to disk atomically."""
    _ensure_history_dir()
    tmp_path = SESSIONS_INDEX_PATH.with_suffix(".tmp")
    tmp_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_path.replace(SESSIONS_INDEX_PATH)


def _session_file_path(session_id: str) -> Path:
    """Return the path for a given session's history file."""
    _ensure_history_dir()
    return HISTORY_DIR / f"{session_id}.jsonl"


def create_session(metadata: Optional[Dict[str, Any]] = None) -> str:
    """Create a new session and return its ID."""
    _ensure_history_dir()
    index = _load_sessions_index()

    session_id = uuid.uuid4().hex
    now = datetime.utcnow().isoformat() + "Z"

    index["sessions"][session_id] = {
        "created_at": now,
        "last_used_at": now,
        "message_count": 0,
        "bytes": 0,
        "status": "active",
        "metadata": metadata or {},
    }

    # Create an empty history file
    history_path = _session_file_path(session_id)
    if not history_path.exists():
        history_path.touch()

    _save_sessions_index(index)
    return session_id


def _trim_session_file(session_id: str, index: Dict[str, Any]) -> None:
    """Trim a session file to respect max messages and file size limits."""
    if not DEFAULT_SESSION_AUTO_TRIM:
        return

    path = _session_file_path(session_id)
    if not path.exists():
        return

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return

    # Keep only the most recent messages according to configured limit
    if len(lines) > DEFAULT_SESSION_MAX_MESSAGES:
        lines = lines[-DEFAULT_SESSION_MAX_MESSAGES :]

    content = "\n".join(lines) + ("\n" if lines else "")

    # Enforce approximate file size limit as well
    encoded = content.encode("utf-8")
    if len(encoded) > DEFAULT_SESSION_MAX_FILE_BYTES:
        # If still too large, drop oldest lines until under limit
        while lines and len("\n".join(lines).encode("utf-8")) > DEFAULT_SESSION_MAX_FILE_BYTES:
            lines.pop(0)
        content = "\n".join(lines) + ("\n" if lines else "")
        encoded = content.encode("utf-8")

    path.write_text(content, encoding="utf-8")

    # Update index metadata
    meta = index.get("sessions", {}).get(session_id)
    if meta is not None:
        meta["message_count"] = len(lines)
        meta["bytes"] = len(encoded)


def append_session_message(session_id: str, role: str, content: str) -> None:
    """Append a message to a session and update index/trim as needed."""
    _ensure_history_dir()
    index = _load_sessions_index()

    if "sessions" not in index or session_id not in index["sessions"]:
        # Unknown session; create basic entry so we don't lose data
        now = datetime.utcnow().isoformat() + "Z"
        index.setdefault("sessions", {})[session_id] = {
            "created_at": now,
            "last_used_at": now,
            "message_count": 0,
            "bytes": 0,
            "status": "active",
            "metadata": {},
        }

    history_path = _session_file_path(session_id)

    event = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    line = json.dumps(event, ensure_ascii=False)
    # Append event
    with history_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    # Update index metadata
    meta = index["sessions"][session_id]
    meta["last_used_at"] = event["timestamp"]
    meta["message_count"] = meta.get("message_count", 0) + 1
    meta["bytes"] = history_path.stat().st_size

    _trim_session_file(session_id, index)
    _save_sessions_index(index)


def load_recent_session_messages(session_id: str, max_messages: Optional[int] = None) -> List[Dict[str, Any]]:
    """Load the most recent messages for a session.

    Returned list is ordered from oldest to newest.
    """
    _ensure_history_dir()
    path = _session_file_path(session_id)
    if not path.exists():
        return []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    if max_messages is None:
        max_messages = DEFAULT_SESSION_MAX_MESSAGES

    # Take only the most recent N lines
    if len(lines) > max_messages:
        lines = lines[-max_messages:]

    messages: List[Dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                messages.append(event)
        except json.JSONDecodeError:
            continue

    return messages


def mark_session_ended(session_id: str, delete: bool = False) -> bool:
    """Mark a session as closed and optionally delete its history file.

    Returns True if the session existed, False otherwise.
    """
    _ensure_history_dir()
    index = _load_sessions_index()
    sessions = index.get("sessions", {})
    if session_id not in sessions:
        return False

    sessions[session_id]["status"] = "closed"
    sessions[session_id]["last_used_at"] = datetime.utcnow().isoformat() + "Z"

    history_path = _session_file_path(session_id)
    if delete and history_path.exists():
        try:
            history_path.unlink()
            sessions[session_id]["bytes"] = 0
            sessions[session_id]["message_count"] = 0
        except Exception:
            # Best effort; keep metadata if delete fails
            pass

    _save_sessions_index(index)
    return True


def _read_file_safe(
    path_arg: str,
    max_bytes: int = 200000,
    encoding: str = "utf-8",
) -> tuple[Optional[str], Optional[Path], Optional[str]]:
    """Read a file from the server base directory with path safety checks.

    Returns:
        (content, full_path, None) on success, or (None, None, error_message) on failure.
    """
    if not path_arg:
        return None, None, "Error: path is required"
    if max_bytes <= 0:
        return None, None, "Error: max_bytes must be a positive integer"

    raw_path = Path(path_arg)
    if raw_path.is_absolute():
        full_path = raw_path
    else:
        full_path = (BASE_DIR / raw_path).resolve()

    base_resolved = BASE_DIR.resolve()
    try:
        full_path.relative_to(base_resolved)
    except ValueError:
        return (
            None,
            None,
            f"Error: access outside the MCP server directory is not allowed.\nBase directory: {base_resolved}",
        )

    if not full_path.exists():
        return None, None, f"Error: file not found: {full_path}"
    if not full_path.is_file():
        return None, None, f"Error: path is not a file: {full_path}"

    try:
        with full_path.open("rb") as f:
            data = f.read(max_bytes + 1)
    except Exception as exc:
        return None, None, f"Error reading file {full_path}: {exc}"

    if len(data) > max_bytes:
        data = data[:max_bytes]

    try:
        text = data.decode(encoding, errors="replace")
    except LookupError:
        return None, None, f"Error: unknown text encoding '{encoding}'"

    return text, full_path, None


# Create MCP server
server = Server("local-llm-mcp-tool")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Lists available tools"""
    return [
        Tool(
            name="generate_text",
            description="Generates text using the Llama model locally",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt to generate text"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum number of tokens to generate",
                        "default": 256
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature for sampling (0.0-2.0)",
                        "default": 0.7
                    },
                    "top_p": {
                        "type": "number",
                        "description": "Top-p sampling (0.0-1.0)",
                        "default": 0.9
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="chat",
            description="Chats with the Llama model using chat format",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "description": "List of messages in format [{\"role\": \"user\", \"content\": \"...\"}]",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "enum": ["user", "assistant", "system"]},
                                "content": {"type": "string"}
                            }
                        }
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum number of tokens to generate",
                        "default": 256
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature for sampling",
                        "default": 0.7
                    }
                },
                "required": ["messages"]
            }
        ),
        Tool(
            name="complete",
            description="Completes text using the Llama model",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to complete"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum number of tokens to generate",
                        "default": 128
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature for sampling",
                        "default": 0.7
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="read_file",
            description=(
                "Reads a local text file from the MCP server's project directory "
                "(relative paths are resolved from the server root and access is "
                "restricted to that tree)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path to the file. Relative paths are resolved from the "
                            "MCP server root directory."
                        ),
                    },
                    "max_bytes": {
                        "type": "integer",
                        "description": (
                            "Maximum number of bytes to read from the file "
                            "(helps avoid huge reads)."
                        ),
                        "default": 200000,
                    },
                    "encoding": {
                        "type": "string",
                        "description": (
                            "Text encoding used to decode the file contents."
                        ),
                        "default": "utf-8",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="analyze_file",
            description=(
                "Reads a local text file and uses the Llama model to analyze it: "
                "purpose, structure, potential issues, and improvements. "
                "Path is relative to the MCP server root; access is restricted to that tree."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file (relative to the MCP server root).",
                    },
                    "instruction": {
                        "type": "string",
                        "description": (
                            "Optional custom instruction for the analysis "
                            "(e.g. 'Focus on security' or 'Summarize in 3 bullet points'). "
                            "If omitted, a general analysis is performed."
                        ),
                    },
                    "max_bytes": {
                        "type": "integer",
                        "description": "Maximum bytes to read from the file.",
                        "default": 200000,
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Text encoding for the file.",
                        "default": "utf-8",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens for the model's analysis.",
                        "default": 512,
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature for sampling.",
                        "default": 0.3,
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="start_session",
            description="Starts a new conversation session and returns a session_id",
            inputSchema={
                "type": "object",
                "properties": {
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata about the session (e.g. purpose, label)",
                    }
                },
            },
        ),
        Tool(
            name="continue_session",
            description="Continues an existing session with a new user message using recent history",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID returned by start_session",
                    },
                    "message": {
                        "type": "string",
                        "description": "The new user message to add to the session",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum number of tokens to generate",
                        "default": 256,
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature for sampling",
                        "default": 0.7,
                    },
                    "top_p": {
                        "type": "number",
                        "description": "Top-p sampling (0.0-1.0)",
                        "default": 0.9,
                    },
                },
                "required": ["session_id", "message"],
            },
        ),
        Tool(
            name="end_session",
            description="Marks a conversation session as ended and optionally deletes its history",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID to end",
                    },
                    "delete": {
                        "type": "boolean",
                        "description": "Whether to delete the stored history for this session",
                        "default": False,
                    },
                },
                "required": ["session_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Executes a tool"""
    try:
        # Session management tools that don't require the model
        if name == "start_session":
            metadata = arguments.get("metadata")
            if metadata is not None and not isinstance(metadata, dict):
                return [TextContent(type="text", text="Error: metadata must be an object if provided")]

            session_id = create_session(metadata=metadata)

            # Persist an initial system event so the history file is never empty
            if metadata:
                meta_str = json.dumps(metadata, ensure_ascii=False)
                content = f"Session started with metadata: {meta_str}"
            else:
                content = "Session started."
            append_session_message(session_id, "system", content)

            return [
                TextContent(
                    type="text",
                    text=(
                        f"Session started.\n\n"
                        f"session_id: {session_id}\n\n"
                        "Use the continue_session tool with this session_id to continue the conversation."
                    ),
                )
            ]

        if name == "end_session":
            session_id = arguments.get("session_id", "")
            delete = bool(arguments.get("delete", False))

            if not session_id:
                return [TextContent(type="text", text="Error: session_id is required")]

            existed = mark_session_ended(session_id, delete=delete)
            if not existed:
                return [TextContent(type="text", text=f"Error: session not found: {session_id}")]

            action = "and deleted" if delete else "and marked as closed"
            return [
                TextContent(
                    type="text",
                    text=f"Session {session_id} has been ended {action}.",
                )
            ]

        if name == "read_file":
            path_arg = arguments.get("path", "")
            max_bytes = int(arguments.get("max_bytes", 200000))
            encoding = arguments.get("encoding", "utf-8")
            content, full_path, err = _read_file_safe(path_arg, max_bytes, encoding)
            if err is not None:
                return [TextContent(type="text", text=err)]
            assert content is not None and full_path is not None
            header = f"Path: {full_path}\nCharacters: {len(content)}"
            body = f"{header}\n\n{content}"
            return [TextContent(type="text", text=body)]

        if name == "analyze_file":
            path_arg = arguments.get("path", "")
            instruction = (arguments.get("instruction") or "").strip()
            max_bytes = int(arguments.get("max_bytes", 200000))
            encoding = arguments.get("encoding", "utf-8")
            max_tokens = int(arguments.get("max_tokens", 512))
            temperature = float(arguments.get("temperature", 0.3))
            content, full_path, err = _read_file_safe(path_arg, max_bytes, encoding)
            if err is not None:
                return [TextContent(type="text", text=err)]
            assert content is not None and full_path is not None
            if not instruction:
                instruction = (
                    "Analyze this file. Describe its purpose, structure, "
                    "and any notable issues or improvements. Be concise but informative."
                )
            prompt = (
                f"{instruction}\n\n"
                f"--- File: {full_path} ---\n\n"
                f"{content}"
            )
            model = load_model()
            chunks, _ = generate_completion(
                model,
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                stop=None,
                streaming=DEFAULT_STREAMING_ENABLED,
                chunk_size=DEFAULT_STREAMING_CHUNK_SIZE,
            )
            return chunks

        # Load model if not already loaded
        model = load_model()

        if name == "generate_text":
            prompt = arguments.get("prompt", "")
            max_tokens = arguments.get("max_tokens", 256)
            temperature = arguments.get("temperature", 0.7)
            top_p = arguments.get("top_p", 0.9)
            
            if not prompt:
                return [TextContent(type="text", text="Error: prompt is required")]
            
            chunks, _ = generate_completion(
                model,
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=None,
                streaming=DEFAULT_STREAMING_ENABLED,
                chunk_size=DEFAULT_STREAMING_CHUNK_SIZE,
            )
            return chunks
        
        elif name == "chat":
            messages = arguments.get("messages", [])
            max_tokens = arguments.get("max_tokens", 256)
            temperature = arguments.get("temperature", 0.7)
            
            if not messages:
                return [TextContent(type="text", text="Error: messages is required")]
            
            # Convert messages to prompt format
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    prompt_parts.append(f"System: {content}")
                elif role == "user":
                    prompt_parts.append(f"User: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")
            
            prompt = "\n".join(prompt_parts) + "\nAssistant:"
            
            chunks, _ = generate_completion(
                model,
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                stop=["User:", "System:"],
                streaming=DEFAULT_STREAMING_ENABLED,
                chunk_size=DEFAULT_STREAMING_CHUNK_SIZE,
            )
            # Strip whitespace from first chunk if present
            if chunks and chunks[0].text:
                chunks[0].text = chunks[0].text.strip()
            return chunks
        
        elif name == "complete":
            text = arguments.get("text", "")
            max_tokens = arguments.get("max_tokens", 128)
            temperature = arguments.get("temperature", 0.7)
            
            if not text:
                return [TextContent(type="text", text="Error: text is required")]
            
            chunks, _ = generate_completion(
                model,
                text,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                stop=None,
                streaming=DEFAULT_STREAMING_ENABLED,
                chunk_size=DEFAULT_STREAMING_CHUNK_SIZE,
            )
            return chunks
        
        elif name == "continue_session":
            session_id = arguments.get("session_id", "")
            message = arguments.get("message", "")
            max_tokens = arguments.get("max_tokens", 256)
            temperature = arguments.get("temperature", 0.7)
            top_p = arguments.get("top_p", 0.9)

            if not session_id:
                return [TextContent(type="text", text="Error: session_id is required")]
            if not message:
                return [TextContent(type="text", text="Error: message is required")]

            # Load recent history for this session
            history_events = load_recent_session_messages(
                session_id,
                max_messages=DEFAULT_SESSION_MAX_MESSAGES,
            )

            prompt_parts: list[str] = []
            for event in history_events:
                role = event.get("role", "user")
                content = event.get("content", "")
                if not content:
                    continue
                if role == "system":
                    prefix = "System"
                elif role == "assistant":
                    prefix = "Assistant"
                else:
                    prefix = "User"
                prompt_parts.append(f"{prefix}: {content}")

            # Add new user message
            prompt_parts.append(f"User: {message}")
            prompt_parts.append("Assistant:")
            prompt = "\n".join(prompt_parts)

            # Generate with streaming support
            chunks, full_response = generate_completion(
                model,
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=["User:", "System:"],
                streaming=DEFAULT_STREAMING_ENABLED,
                chunk_size=DEFAULT_STREAMING_CHUNK_SIZE,
            )

            # Strip whitespace from full response before persisting
            full_response = full_response.strip()

            # Persist new turn in session history (always use full accumulated text)
            append_session_message(session_id, "user", message)
            append_session_message(session_id, "assistant", full_response)

            # Strip whitespace from first chunk if present
            if chunks and chunks[0].text:
                chunks[0].text = chunks[0].text.strip()

            return chunks
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing tool: {str(e)}")]


async def main():
    """Main function"""
    # Load model on initialization (optional, can be lazy)
    try:
        if DEFAULT_MODEL_PATH and os.path.exists(DEFAULT_MODEL_PATH):
            load_model()
    except Exception as e:
        print(f"Warning: Could not load model on initialization: {e}", file=sys.stderr)
        print("The model will be loaded when the first tool is called.", file=sys.stderr)
    
    # Start MCP server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
