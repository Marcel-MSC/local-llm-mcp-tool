#!/usr/bin/env python3
"""
Servidor MCP com integração Llama para execução local
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv

try:
    from llama_cpp import Llama
except ImportError:
    print("Erro: llama-cpp-python não está instalado.")
    print("Instale com: pip install llama-cpp-python")
    sys.exit(1)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Erro: biblioteca MCP não está instalada.")
    print("Instale com: pip install mcp")
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


def load_model(model_path: Optional[str] = None) -> Llama:
    """Carrega o modelo Llama"""
    global llama_model
    
    if llama_model is not None:
        return llama_model
    
    path = model_path or DEFAULT_MODEL_PATH
    
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


# Cria o servidor MCP
server = Server("local-llm-mcp-tool")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Lista as ferramentas disponíveis"""
    return [
        Tool(
            name="generate_text",
            description="Gera texto usando o modelo Llama localmente",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "O prompt para gerar texto"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Número máximo de tokens a gerar",
                        "default": 256
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperatura para sampling (0.0-2.0)",
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
            description="Conversa com o modelo Llama usando formato de chat",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "description": "Lista de mensagens no formato [{\"role\": \"user\", \"content\": \"...\"}]",
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
                        "description": "Número máximo de tokens a gerar",
                        "default": 256
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperatura para sampling",
                        "default": 0.7
                    }
                },
                "required": ["messages"]
            }
        ),
        Tool(
            name="complete",
            description="Completa um texto usando o modelo Llama",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "O texto a ser completado"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Número máximo de tokens a gerar",
                        "default": 128
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperatura para sampling",
                        "default": 0.7
                    }
                },
                "required": ["text"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Executa uma ferramenta"""
    try:
        # Carrega o modelo se ainda não foi carregado
        model = load_model()
        
        if name == "generate_text":
            prompt = arguments.get("prompt", "")
            max_tokens = arguments.get("max_tokens", 256)
            temperature = arguments.get("temperature", 0.7)
            top_p = arguments.get("top_p", 0.9)
            
            if not prompt:
                return [TextContent(type="text", text="Erro: prompt é obrigatório")]
            
            output = model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                echo=False,
                stop=["\n\n"]
            )
            
            generated_text = output["choices"][0]["text"]
            return [TextContent(type="text", text=generated_text)]
        
        elif name == "chat":
            messages = arguments.get("messages", [])
            max_tokens = arguments.get("max_tokens", 256)
            temperature = arguments.get("temperature", 0.7)
            
            if not messages:
                return [TextContent(type="text", text="Erro: messages é obrigatório")]
            
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
            
            response = output["choices"][0]["text"].strip()
            return [TextContent(type="text", text=response)]
        
        elif name == "complete":
            text = arguments.get("text", "")
            max_tokens = arguments.get("max_tokens", 128)
            temperature = arguments.get("temperature", 0.7)
            
            if not text:
                return [TextContent(type="text", text="Erro: text é obrigatório")]
            
            output = model(
                text,
                max_tokens=max_tokens,
                temperature=temperature,
                echo=False
            )
            
            completion = output["choices"][0]["text"]
            return [TextContent(type="text", text=completion)]
        
        else:
            return [TextContent(type="text", text=f"Ferramenta desconhecida: {name}")]
    
    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"Erro: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Erro ao executar ferramenta: {str(e)}")]


async def main():
    """Função principal"""
    # Carrega o modelo na inicialização (opcional, pode ser lazy)
    try:
        if DEFAULT_MODEL_PATH and os.path.exists(DEFAULT_MODEL_PATH):
            load_model()
    except Exception as e:
        print(f"Aviso: Não foi possível carregar o modelo na inicialização: {e}", file=sys.stderr)
        print("O modelo será carregado quando a primeira ferramenta for chamada.", file=sys.stderr)
    
    # Inicia o servidor MCP usando stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
