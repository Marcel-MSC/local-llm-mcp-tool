# Local LLM MCP Tool - Fly.io deployment
# Uses CPU-only llama-cpp-python (Fly.io runs Linux)

FROM python:3.11-slim

WORKDIR /app

# Install system deps for llama-cpp-python (minimal for CPU pre-built wheel)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python deps (llama-cpp-python excluded - uses wheel below)
RUN pip install --no-cache-dir -r requirements.txt

# Install llama-cpp-python from pre-built CPU wheel (avoids compilation in container)
RUN pip install --no-cache-dir llama-cpp-python \
    --index-url https://abetlen.github.io/llama-cpp-python/whl/cpu \
    --extra-index-url https://pypi.org/simple/

# Copy application code
COPY server_fastmcp.py server_http.py download_model.py entrypoint.sh ./
COPY .env.example ./

# Create models directory (for MODEL_PATH when using MODEL_URL)
RUN mkdir -p /app/models && chmod +x /app/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
