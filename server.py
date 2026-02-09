#!/usr/bin/env python3
"""
MCP server with Llama integration for local execution
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

# Global model instance
llama_model: Optional[Llama] = None


def load_model(model_path: Optional[str] = None) -> Llama:
    """Loads the Llama model"""
    global llama_model
    
    if llama_model is not None:
        return llama_model
    
    path = model_path or DEFAULT_MODEL_PATH
    
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
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Executes a tool"""
    try:
        # Load model if not already loaded
        model = load_model()
        
        if name == "generate_text":
            prompt = arguments.get("prompt", "")
            max_tokens = arguments.get("max_tokens", 256)
            temperature = arguments.get("temperature", 0.7)
            top_p = arguments.get("top_p", 0.9)
            
            if not prompt:
                return [TextContent(type="text", text="Error: prompt is required")]
            
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
                return [TextContent(type="text", text="Error: text is required")]
            
            output = model(
                text,
                max_tokens=max_tokens,
                temperature=temperature,
                echo=False
            )
            
            completion = output["choices"][0]["text"]
            return [TextContent(type="text", text=completion)]
        
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
