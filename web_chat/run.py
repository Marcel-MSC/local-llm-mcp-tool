#!/usr/bin/env python3
"""
Run the web chat server. Execute from project root:
  python web_chat/run.py
"""
import sys
from pathlib import Path

# Ensure project root is in path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Custom log format with timestamp (dd-mm-yyyy HH:MM)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s: %(message)s",
            "datefmt": "%d-%m-%Y %H:%M",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s - %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            "datefmt": "%d-%m-%Y %H:%M",
            "use_colors": False,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

if __name__ == "__main__":
    import uvicorn

    print("\n  Local LLM Web Chat: http://localhost:8000\n")
    uvicorn.run(
        "web_chat.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(ROOT), str(ROOT / "web_chat")],
        log_config=LOGGING_CONFIG,
    )
