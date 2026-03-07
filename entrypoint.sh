#!/bin/sh
set -e

# Download model if MODEL_URL is set and MODEL_PATH doesn't exist or is empty
if [ -n "$MODEL_URL" ] && { [ -z "$MODEL_PATH" ] || [ ! -f "$MODEL_PATH" ]; }; then
  echo "Downloading model from $MODEL_URL..."
  DEST="${MODEL_PATH:-/app/models/model.gguf}"
  mkdir -p "$(dirname "$DEST")"
  curl -fSL -o "$DEST" "$MODEL_URL"
  export MODEL_PATH="$DEST"
  echo "Model saved to $MODEL_PATH"
fi

# MODEL_PATH must be set (via env or fly secrets)
if [ -z "$MODEL_PATH" ]; then
  echo "Error: MODEL_PATH or MODEL_URL must be set. Use: fly secrets set MODEL_URL=https://... or MODEL_PATH=..."
  exit 1
fi

if [ ! -f "$MODEL_PATH" ]; then
  echo "Error: Model file not found at $MODEL_PATH"
  exit 1
fi

exec python server_http.py
