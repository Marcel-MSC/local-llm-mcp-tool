# Deploy to Fly.io

This guide covers deploying the Local LLM MCP Tool to Fly.io as a remote MCP server.

## Prerequisites

- [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/) installed
- Fly.io account

## Quick Deploy

1. **From the project root**, run:

   ```bash
   fly launch
   ```

   - Choose an app name or let Fly generate one
   - Don't add a Postgres or Redis (we don't need them)
   - Say **No** to deploy immediately (we need to set secrets first)

2. **Set the model URL** (required). Use a small model for Fly.io's free tier, e.g. Llama 3.2 1B:

   ```bash
   fly secrets set MODEL_URL="https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
   ```

3. **Deploy**:

   ```bash
   fly deploy
   ```

4. **Connect your MCP client** to:

   ```
   https://<your-app-name>.fly.dev/mcp
   ```

   Example for Cursor/Claude: add a remote MCP server with transport `http` and the URL above.

## Configuration

### Secrets (sensitive)

- `MODEL_URL` – Hugging Face (or other) URL to download a GGUF model at startup  
  Example: `https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf`

### Optional env vars (in `fly.toml` or `fly secrets set`)

- `CONTEXT_SIZE` – Max context (default: 2048)
- `N_THREADS` – CPU threads (default: 4)
- `N_GPU_LAYERS` – GPU layers (default: 0, CPU only on Fly)

## Machine size

The default `fly.toml` uses 2GB RAM and 2 shared CPUs, which works for small models (1B–3B). For larger models, adjust `[[vm]]` in `fly.toml` or run:

```bash
fly scale memory 4096
```

## Endpoints

| Path   | Description                    |
|--------|--------------------------------|
| `/`    | Health check (returns `{"status":"ok"}`) |
| `/mcp` | MCP Streamable HTTP endpoint   |

## Troubleshooting

### Deployment fails

- Check logs: `fly logs`
- Confirm `MODEL_URL` is set: `fly secrets list`
- Ensure the URL returns a valid GGUF file

### Out of memory

- Switch to a smaller model (e.g. Llama 3.2 1B Q4_K_M)
- Increase memory: `fly scale memory 4096`

### Slow first request

- The model loads on first use; expect a delay of tens of seconds
- Consider keeping one machine running: set `min_machines_running = 1` in `fly.toml`
