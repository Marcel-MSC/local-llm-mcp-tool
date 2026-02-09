#!/usr/bin/env python3
"""
Servidor MCP com integração Llama usando FastMCP (versão alternativa mais simples)
"""
import os
import sys
from typing import Optional
from dotenv import load_dotenv

try:
    from llama_cpp import Llama
except ImportError:
    print("Erro: llama-cpp-python não está instalado.", file=sys.stderr)
    print("Instale com: pip install llama-cpp-python", file=sys.stderr)
    sys.exit(1)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Erro: biblioteca MCP não está instalada.", file=sys.stderr)
    print("Instale com: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Carrega variáveis de ambiente
load_dotenv()

# Configurações padrão
DEFAULT_MODEL_PATH = os.getenv("MODEL_PATH", "")
DEFAULT_CONTEXT_SIZE = int(os.getenv("CONTEXT_SIZE", "2048"))
DEFAULT_N_THREADS = int(os.getenv("N_THREADS", "4"))
DEFAULT_N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", "0"))

# Instância global do modelo
llama_model: Optional[Llama] = None


def get_model() -> Llama:
    """Obtém ou carrega o modelo Llama"""
    global llama_model
    
    if llama_model is not None:
        return llama_model
    
    path = DEFAULT_MODEL_PATH
    
    if not path or not os.path.exists(path):
        error_msg = f"Erro: Modelo não encontrado em {path}\nPor favor, configure MODEL_PATH no arquivo .env\nOu baixe um modelo GGUF de: https://huggingface.co/models?library=gguf"
        print(error_msg, file=sys.stderr)
        raise FileNotFoundError(f"Modelo não encontrado: {path}")
    
    print(f"Carregando modelo de: {path}", file=sys.stderr)
    
    try:
        llama_model = Llama(
            model_path=path,
            n_ctx=DEFAULT_CONTEXT_SIZE,
            n_threads=DEFAULT_N_THREADS,
            n_gpu_layers=DEFAULT_N_GPU_LAYERS,
            verbose=False
        )
        print("Modelo carregado com sucesso!", file=sys.stderr)
        return llama_model
    except Exception as e:
        print(f"Erro ao carregar modelo: {e}", file=sys.stderr)
        raise


# Cria o servidor FastMCP
mcp = FastMCP("Local LLM MCP Tool")


@mcp.tool()
def generate_text(
    prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9
) -> str:
    """Gera texto usando o modelo Llama localmente"""
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
    """Conversa com o modelo Llama usando formato de chat"""
    model = get_model()
    
    # Converte mensagens para formato de prompt
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
    """Completa um texto usando o modelo Llama"""
    model = get_model()
    
    output = model(
        text,
        max_tokens=max_tokens,
        temperature=temperature,
        echo=False
    )
    
    return output["choices"][0]["text"]


if __name__ == "__main__":
    # Tenta carregar o modelo na inicialização (opcional)
    try:
        if DEFAULT_MODEL_PATH and os.path.exists(DEFAULT_MODEL_PATH):
            get_model()
    except Exception as e:
        print(f"Aviso: Não foi possível carregar o modelo na inicialização: {e}", file=sys.stderr)
        print("O modelo será carregado quando a primeira ferramenta for chamada.", file=sys.stderr)
    
    # Inicia o servidor usando stdio
    mcp.run(transport="stdio")
