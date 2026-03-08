"""
LLM client for web chat - wraps server model and tracks metrics.
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path so we can import from server
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

# Metrics storage
METRICS_FILE = Path(__file__).parent / "data" / "metrics.json"
UPLOADS_DIR = Path(__file__).parent / "uploads"


def _ensure_data_dirs():
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    if not METRICS_FILE.exists():
        METRICS_FILE.write_text('{"sessions": [], "summary": {}}', encoding="utf-8")


def _load_metrics() -> dict:
    _ensure_data_dirs()
    try:
        return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"sessions": [], "summary": {}}


def _save_metrics(data: dict):
    _ensure_data_dirs()
    METRICS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def record_metrics(
    session_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    response_time_ms: float,
    model_name: str,
):
    """Record a chat completion for dashboard metrics."""
    data = _load_metrics()
    sessions = data.setdefault("sessions", [])
    sessions.append({
        "session_id": session_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "response_time_ms": round(response_time_ms, 2),
        "model": model_name,
    })
    # Keep last 500 entries
    if len(sessions) > 500:
        sessions[:] = sessions[-500:]

    summary = data.setdefault("summary", {})
    summary["total_prompt_tokens"] = summary.get("total_prompt_tokens", 0) + prompt_tokens
    summary["total_completion_tokens"] = summary.get("total_completion_tokens", 0) + completion_tokens
    summary["total_tokens"] = summary.get("total_tokens", 0) + prompt_tokens + completion_tokens
    summary["total_requests"] = summary.get("total_requests", 0) + 1
    summary["total_response_time_ms"] = summary.get("total_response_time_ms", 0) + response_time_ms

    _save_metrics(data)


def get_model(model_path: Optional[str] = None) -> Any:
    """Load and return the Llama model from server."""
    from server import load_model
    return load_model(model_path=model_path)


def get_available_models() -> List[Dict[str, str]]:
    """List available GGUF models."""
    from server import get_available_models as _get
    return _get()


def get_model_info(model_path: Optional[str] = None) -> Dict[str, Any]:
    """Return current model path and config. model_path overrides for display."""
    from server import get_current_model_path

    current = get_current_model_path()
    path = model_path or current or os.getenv("MODEL_PATH", "")
    return {
        "model_path": path,
        "model_name": Path(path).name if path else "Nenhum modelo carregado",
        "context_size": int(os.getenv("CONTEXT_SIZE", "2048")),
        "n_threads": int(os.getenv("N_THREADS", "4")),
        "n_gpu_layers": int(os.getenv("N_GPU_LAYERS", "0")),
    }


def chat(
    messages: List[Dict[str, str]],
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
    session_id: str = "",
    model_path: Optional[str] = None,
) -> tuple[str, Dict[str, Any]]:
    """
    Send chat messages to the model. Returns (response_text, metrics).
    """
    from server import load_model

    model = load_model(model_path=model_path)
    model_info = get_model_info()

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

    start = time.perf_counter()
    output = model(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        echo=False,
        stop=["User:", "System:"],
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    text = output["choices"][0]["text"].strip()
    usage = output.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    if prompt_tokens == 0 and completion_tokens == 0:
        # Estimate tokens if not provided (~4 chars per token)
        prompt_tokens = max(1, len(prompt) // 4)
        completion_tokens = max(1, len(text) // 4)

    record_metrics(
        session_id=session_id or "web",
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        response_time_ms=elapsed_ms,
        model_name=model_info["model_name"],
    )

    metrics = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "response_time_ms": round(elapsed_ms, 2),
    }
    return text, metrics


def create_session(metadata: Optional[Dict[str, Any]] = None) -> str:
    """Create a new session. Returns session_id."""
    from server import create_session as _create_session

    return _create_session(metadata=metadata)


def continue_session(
    session_id: str,
    message: str,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
    model_path: Optional[str] = None,
) -> tuple[str, Dict[str, Any]]:
    """Continue a session with history persisted on server. Returns (response_text, metrics)."""
    from server import (
        load_model,
        load_recent_session_messages,
        append_session_message,
        DEFAULT_SESSION_MAX_MESSAGES,
    )

    model = load_model(model_path=model_path)
    model_info = get_model_info()

    history_events = load_recent_session_messages(
        session_id, max_messages=DEFAULT_SESSION_MAX_MESSAGES
    )

    prompt_parts = []
    for event in history_events:
        role = event.get("role", "user")
        content = event.get("content", "")
        if not content:
            continue
        prefix = "System" if role == "system" else ("Assistant" if role == "assistant" else "User")
        prompt_parts.append(f"{prefix}: {content}")

    prompt_parts.append(f"User: {message}")
    prompt_parts.append("Assistant:")
    prompt = "\n".join(prompt_parts)

    start = time.perf_counter()
    output = model(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        echo=False,
        stop=["User:", "System:"],
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    text = output["choices"][0]["text"].strip()
    usage = output.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    if prompt_tokens == 0 and completion_tokens == 0:
        prompt_tokens = max(1, len(prompt) // 4)
        completion_tokens = max(1, len(text) // 4)

    append_session_message(session_id, "user", message)
    append_session_message(session_id, "assistant", text)

    record_metrics(
        session_id=session_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        response_time_ms=elapsed_ms,
        model_name=model_info["model_name"],
    )

    metrics = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "response_time_ms": round(elapsed_ms, 2),
    }
    return text, metrics


def analyze_file(
    file_path: str,
    instruction: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.3,
    session_id: str = "",
    model_path: Optional[str] = None,
) -> tuple[str, Dict[str, Any]]:
    """Read and analyze a file with the model. Returns (analysis_text, metrics)."""
    from server import _read_file_safe, load_model

    content, full_path, err = _read_file_safe(file_path, max_bytes=200000)
    if err:
        return err, {}

    model = load_model(model_path=model_path)
    model_info = get_model_info()

    inst = instruction or (
        "Analyze this file. Describe its purpose, structure, "
        "and any notable issues or improvements. Be concise but informative."
    )
    prompt = f"{inst}\n\n--- File: {full_path} ---\n\n{content}"

    start = time.perf_counter()
    output = model(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=0.9,
        echo=False,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    text = output["choices"][0]["text"].strip()
    usage = output.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    if prompt_tokens == 0 and completion_tokens == 0:
        prompt_tokens = max(1, len(prompt) // 4)
        completion_tokens = max(1, len(text) // 4)

    record_metrics(
        session_id=session_id or "file_analysis",
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        response_time_ms=elapsed_ms,
        model_name=model_info["model_name"],
    )

    metrics = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "response_time_ms": round(elapsed_ms, 2),
    }
    return text, metrics


def get_dashboard_data() -> Dict[str, Any]:
    """Return aggregated metrics for the dashboard."""
    data = _load_metrics()
    sessions = data.get("sessions", [])
    summary = data.get("summary", {})

    total_requests = summary.get("total_requests", 0)
    avg_response_ms = (
        summary["total_response_time_ms"] / total_requests
        if total_requests > 0
        else 0
    )

    return {
        "summary": {
            "total_prompt_tokens": summary.get("total_prompt_tokens", 0),
            "total_completion_tokens": summary.get("total_completion_tokens", 0),
            "total_tokens": summary.get("total_tokens", 0),
            "total_requests": total_requests,
            "avg_response_time_ms": round(avg_response_ms, 2),
            "total_response_time_ms": summary.get("total_response_time_ms", 0),
        },
        "recent_sessions": sessions[-50:][::-1],
    }
