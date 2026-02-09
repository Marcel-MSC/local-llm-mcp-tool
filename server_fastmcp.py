#!/usr/bin/env python3
"""
MCP server with Llama integration using FastMCP (simpler alternative version)
"""
import os
import sys
from typing import Optional
from dotenv import load_dotenv

try:
    from llama_cpp import Llama
except ImportError:
    print("Error: llama-cpp-python is not installed.", file=sys.stderr)
    print("Install with: pip install llama-cpp-python", file=sys.stderr)
    sys.exit(1)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: MCP library is not installed.", file=sys.stderr)
    print("Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Load environment variables
load_dotenv()

# Default configurations
DEFAULT_MODEL_PATH = os.getenv("MODEL_PATH", "")
DEFAULT_CONTEXT_SIZE = int(os.getenv("CONTEXT_SIZE", "2048"))
DEFAULT_N_THREADS = int(os.getenv("N_THREADS", "4"))
DEFAULT_N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", "0"))

# Global model instance
llama_model: Optional[Llama] = None


def get_model() -> Llama:
    """Gets or loads the Llama model"""
    global llama_model
    
    if llama_model is not None:
        return llama_model
    
    path = DEFAULT_MODEL_PATH
    
    if not path or not os.path.exists(path):
        error_msg = f"Error: Model not found at {path}\nPlease configure MODEL_PATH in the .env file\nOr download a GGUF model from: https://huggingface.co/models?library=gguf"
        print(error_msg, file=sys.stderr)
        raise FileNotFoundError(f"Model not found: {path}")
    
    print(f"Loading model from: {path}", file=sys.stderr)
    
    try:
        llama_model = Llama(
            model_path=path,
            n_ctx=DEFAULT_CONTEXT_SIZE,
            n_threads=DEFAULT_N_THREADS,
            n_gpu_layers=DEFAULT_N_GPU_LAYERS,
            verbose=False
        )
        print("Model loaded successfully!", file=sys.stderr)
        return llama_model
    except Exception as e:
        print(f"Error loading model: {e}", file=sys.stderr)
        raise


# Create FastMCP server
mcp = FastMCP("Local LLM MCP Tool")


@mcp.tool()
def generate_text(
    prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9
) -> str:
    """Generates text using the Llama model locally"""
    model = get_model()
    
    output = model(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        echo=False,
        stop=["\n\n"]
    )
    
    return output["choices"][0]["text"]


@mcp.tool()
def chat(
    messages: list[dict],
    max_tokens: int = 256,
    temperature: float = 0.7
) -> str:
    """Chats with the Llama model using chat format"""
    model = get_model()
    
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
    
    output = model(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        echo=False,
        stop=["User:", "System:"]
    )
    
    return output["choices"][0]["text"].strip()


@mcp.tool()
def complete(
    text: str,
    max_tokens: int = 128,
    temperature: float = 0.7
) -> str:
    """Completes text using the Llama model"""
    model = get_model()
    
    output = model(
        text,
        max_tokens=max_tokens,
        temperature=temperature,
        echo=False
    )
    
    return output["choices"][0]["text"]


if __name__ == "__main__":
    # Try to load model on initialization (optional)
    try:
        if DEFAULT_MODEL_PATH and os.path.exists(DEFAULT_MODEL_PATH):
            get_model()
    except Exception as e:
        print(f"Warning: Could not load model on initialization: {e}", file=sys.stderr)
        print("The model will be loaded when the first tool is called.", file=sys.stderr)
    
    # Start server using stdio
    mcp.run(transport="stdio")
