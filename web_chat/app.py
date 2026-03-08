"""
Local LLM Web Chat - FastAPI application
"""
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Add parent to path for server imports
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

app = FastAPI(title="Local LLM Web Chat")

# Templates and static
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# --- Request/Response models ---


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    save_history: bool = True
    session_id: str | None = None
    model_path: str | None = None


class ConfigUpdate(BaseModel):
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None


# --- LLM client (lazy import to avoid loading model at startup) ---


def get_llm():
    from web_chat.llm_client import (
        chat as llm_chat,
        analyze_file as llm_analyze_file,
        create_session as llm_create_session,
        continue_session as llm_continue_session,
        get_model_info,
        get_available_models,
        get_dashboard_data,
    )
    return llm_chat, llm_analyze_file, llm_create_session, llm_continue_session, get_model_info, get_available_models, get_dashboard_data


# --- Routes ---


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main chat page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """Configuration page."""
    _, _, _, _, get_model_info, _, _ = get_llm()
    try:
        info = get_model_info()
    except Exception as e:
        info = {"model_name": "Erro ao carregar", "error": str(e)}
    return templates.TemplateResponse("config.html", {"request": request, "model_info": info})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page."""
    _, _, _, _, _, _, get_dashboard_data = get_llm()
    try:
        data = get_dashboard_data()
    except Exception:
        data = {"summary": {}, "recent_sessions": []}
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "dashboard": data}
    )


# --- API ---


@app.get("/api/model")
async def api_model():
    """Get current model info."""
    try:
        _, _, _, _, get_model_info, _, _ = get_llm()
        return get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def api_models():
    """List available GGUF models."""
    try:
        _, _, _, _, _, get_available_models, _ = get_llm()
        return {"models": get_available_models()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ModelSwitchRequest(BaseModel):
    model_path: str


@app.post("/api/model/switch")
async def api_model_switch(req: ModelSwitchRequest):
    """Load/switch to the specified model. Blocks until loaded (can take 1-2 min)."""
    path = (req.model_path or "").strip()
    if not path:
        raise HTTPException(status_code=400, detail="model_path is required")
    try:
        from server import load_model
        load_model(model_path=path)
        return {"status": "ok", "model_path": path}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def api_chat(request: ChatRequest):
    """Send chat messages and get response."""
    try:
        llm_chat, _, llm_create_session, llm_continue_session, _, _, _ = get_llm()
        if request.save_history:
            if request.session_id:
                text, metrics = llm_continue_session(
                    session_id=request.session_id,
                    message=request.messages[-1].content if request.messages else "",
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    model_path=request.model_path,
                )
                return {"response": text, "metrics": metrics, "session_id": request.session_id}
            else:
                from server import append_session_message
                session_id = llm_create_session(metadata={"source": "web_chat"})
                messages = [{"role": m.role, "content": m.content} for m in request.messages]
                text, metrics = llm_chat(
                    messages=messages,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    session_id=session_id,
                    model_path=request.model_path,
                )
                user_content = messages[-1].get("content", "") if messages else ""
                append_session_message(session_id, "user", user_content)
                append_session_message(session_id, "assistant", text)
                return {"response": text, "metrics": metrics, "session_id": session_id}
        else:
            messages = [{"role": m.role, "content": m.content} for m in request.messages]
            text, metrics = llm_chat(
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                session_id="no_history",
                model_path=request.model_path,
            )
            return {"response": text, "metrics": metrics, "session_id": None}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail="Modelo não encontrado. Configure MODEL_PATH no .env")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    """Upload a file for analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo inválido")

    ext = Path(file.filename).suffix.lower()
    allowed = {".txt", ".md", ".py", ".js", ".json", ".html", ".css", ".yaml", ".yml", ".toml"}
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não suportado. Permitidos: {', '.join(sorted(allowed))}",
        )

    safe_name = f"{uuid.uuid4().hex[:12]}_{file.filename}"
    save_path = UPLOADS_DIR / safe_name
    content = await file.read()
    if len(content) > 500_000:
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máx. 500KB)")

    save_path.write_bytes(content)

    # Path relative to project root for server
    rel_path = f"web_chat/uploads/{safe_name}"
    return {"path": rel_path, "filename": file.filename}


@app.post("/api/analyze")
async def api_analyze(
    path: str = Form(...),
    instruction: str = Form(""),
    max_tokens: int = Form(512),
    temperature: float = Form(0.3),
    model_path: str = Form(""),
):
    """Analyze an uploaded file."""
    try:
        _, llm_analyze_file, _, _, _, _, _ = get_llm()
        text, metrics = llm_analyze_file(
            file_path=path,
            instruction=instruction.strip() or None,
            max_tokens=max_tokens,
            temperature=temperature,
            model_path=model_path.strip() or None,
        )
        return {"analysis": text, "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard")
async def api_dashboard():
    """Get dashboard metrics."""
    try:
        _, _, _, _, _, _, get_dashboard_data = get_llm()
        return get_dashboard_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
async def api_config():
    """Get current config (from env)."""
    return {
        "MODEL_PATH": os.getenv("MODEL_PATH", ""),
        "CONTEXT_SIZE": int(os.getenv("CONTEXT_SIZE", "2048")),
        "N_THREADS": int(os.getenv("N_THREADS", "4")),
        "N_GPU_LAYERS": int(os.getenv("N_GPU_LAYERS", "0")),
    }


@app.get("/api/sessions")
async def api_sessions():
    """List all conversation sessions (from server history)."""
    try:
        from server import _load_sessions_index

        data = _load_sessions_index()
        sessions = data.get("sessions", {})
        items = [
            {
                "id": sid,
                "created_at": meta.get("created_at", ""),
                "last_used_at": meta.get("last_used_at", ""),
                "message_count": meta.get("message_count", 0),
                "status": meta.get("status", "active"),
            }
            for sid, meta in sessions.items()
        ]
        items.sort(key=lambda x: x["last_used_at"], reverse=True)
        return {"sessions": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/messages")
async def api_session_messages(session_id: str):
    """Get messages for a session."""
    try:
        from server import load_recent_session_messages

        events = load_recent_session_messages(session_id)
        messages = [
            {"role": e.get("role", "user"), "content": e.get("content", "")}
            for e in events
            if e.get("role") in ("user", "assistant")
        ]
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
