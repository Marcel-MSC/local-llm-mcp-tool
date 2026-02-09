# Future Ideas and Evolution

Direct answers and ideas for what can be developed from the current server.

---

## 1. Internet or Local Only?

**Inference (generate text, chat, complete): 100% local.**

- The model runs on your PC (CPU or GPU). No prompt or response data leaves your machine.
- No cloud API usage, no credits consumed, works offline after the model is installed.

**Internet is only used for:**

- Downloading the model (once), e.g., with `download_model.py` or Hugging Face.
- If you add tools that query APIs in the future (e.g., search news), then there would be internet access only in those functions.

**Summary:** The MCP itself runs only locally; internet only for downloading the model (and optionally in extra tools you create).

---

## 2. Leveraging MCP Performance

**Already have:**

- Model loaded once and reused (doesn't reload on each call).
- Configuration via `.env`: `N_THREADS`, `N_GPU_LAYERS`, `CONTEXT_SIZE`.

**What you can do:**

| Action | Where | Effect |
|--------|-------|--------|
| Use GPU | `.env`: `N_GPU_LAYERS=-1` (or e.g., 32) | Much faster if you have NVIDIA. |
| Adjust threads | `.env`: `N_THREADS=8` (or number of cores) | Better CPU usage. |
| Smaller context if not needed | `.env`: `CONTEXT_SIZE=1024` | Less RAM and sometimes faster. |
| Smaller model | Use 1B/3B instead of 7B+ | Faster responses. |
| Fewer tokens per response | Use smaller `max_tokens` in tools | Faster response. |

**Possible code evolutions:**

- **Streaming:** send tokens as they come (instead of waiting for the full response) to appear faster in Cursor.
- **Response cache:** for the same prompt, return cached result (useful in repetitive flows).
- **Request queue:** if multiple calls arrive, process in order without blocking.

---

## 3. What Else Can We Develop?

### Context and Conversation History

**Today:**

- The **chat** tool already receives a list of messages (`user`, `assistant`, `system`). The caller (e.g., Cursor) can build this history and send it each time.
- The server doesn't keep state between calls: each request is independent.

**What can be added:**

1. **History on Client (Cursor)**  
   Cursor can send all previous messages in the `messages` array with each new question. This way the model "sees" the history without the server needing to store anything.

2. **History on Server (Session)**  
   - Keep in memory a list of messages per "session" (e.g., an ID per conversation).
   - New tool, e.g.: `chat_with_session(session_id, new_message)` that:
     - Loads the session history.
     - Adds the new message.
     - Calls the model.
     - Saves the response to history and returns.
   - Optional: persist to file (e.g., JSON per session) to not lose on server restart.

3. **Persistent Context**  
   - Tool to "save context" (e.g., conversation summary or last N messages).
   - Another tool to "load context" before continuing chat.
   - Can be in file or a simple database (SQLite).

### Other Useful Ideas

| Idea | Description |
|------|-------------|
| **Streaming** | Token-by-token response; in MCP this can be via SSE or partial messages, if Cursor supports it. |
| **RAG (Documents)** | Tool that loads PDFs/texts, generates embeddings (if model supports) or uses text as context and answers based on them. |
| **Multiple Models** | `.env` or parameter to choose between multiple GGUF files (e.g., one fast and one larger). |
| **Functions/Tools in Model** | Use chat format with "function calling" and expose in MCP as tools the model itself can "call". |
| **Long Conversation Summary** | Tool that receives many messages and returns a summary to use as context in subsequent calls. |
| **Web Search (Optional)** | New tool that calls a search API and passes the result as context to Llama; then it would use internet only in that tool. |

---

## 4. Suggested Next Steps (by Priority)

1. **Adjust `.env`** for GPU (`N_GPU_LAYERS`) and `N_THREADS` according to your PC.
2. **History on Server:** implement `chat_with_session` with in-memory sessions (and later optionally persist to file).
3. **Streaming:** if the client (Cursor) supports it, send the response in chunks.
4. **Simple RAG:** tool "ask about a document" (load text and use as prompt context).

If you want, we can start with one of these: for example "save context / conversation history" on the server (sessions + option to save to file). Just say which part you want to start with (history, streaming, or RAG) and we'll proceed with that in the `server.py` code.  

---

**Quick Summary**

- **Internet:** only for downloading model; inference 100% local.
- **Performance:** GPU and `N_THREADS` in `.env`; model already stays loaded; can evolve with streaming and cache.
- **Context/History:** today the client sends history in `chat`; can evolve with sessions and persistence on server.
- **Others:** streaming, RAG, multiple models, function calling, conversation summary.
