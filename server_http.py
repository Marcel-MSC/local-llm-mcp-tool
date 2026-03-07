#!/usr/bin/env python3
"""
MCP server with HTTP/Streamable HTTP transport for Fly.io and remote deployment.
Mounts the FastMCP server at /mcp and adds a health endpoint at / for Fly.io checks.
"""
import os
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount

# Import the FastMCP instance and tools from server_fastmcp
from server_fastmcp import mcp


async def health(_request):
    """Health check endpoint for Fly.io"""
    return JSONResponse({"status": "ok", "service": "local-llm-mcp"})


# Create Starlette app with health route and MCP mount
app = Starlette(
    routes=[
        Route("/", health),
        Mount("/mcp", app=mcp.streamable_http_app()),
    ],
)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
