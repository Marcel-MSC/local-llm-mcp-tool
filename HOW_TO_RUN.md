# How to Run the Application

## 1. Install Project Dependencies

Yes, you should install what's in `requirements.txt`. You already installed `llama-cpp-python`; the command below installs the rest (MCP, pydantic, python-dotenv, etc.):

```bash
cd local-llm-mcp-tool
pip install -r requirements.txt
```

pip will only install what's missing; already installed packages will be kept.

---

## 2. Configure the Model

If you don't have a GGUF model yet:

```bash
copy .env.example .env
```

Edit the `.env` file and set your model path:

```
MODEL_PATH=C:\path\to\your\model.gguf
```

If you don't have a model, download one:

```bash
python download_model.py
```

Then, in `.env`, set the path to the downloaded file (e.g., `models\ModelName.gguf`).

---

## 3. Test (Optional)

```bash
python test_server.py
```

If it shows "Tudo pronto!" (All ready!), you can proceed to the next step.

---

## 4. Run the MCP Server

**Option A - Standard Server:**

```bash
python server.py
```

**Option B - FastMCP Server (simpler):**

```bash
python server_fastmcp.py
```

The server will run and wait for connections (e.g., from Cursor). To stop: `Ctrl+C`.

---

## 5. Use with Cursor (Step by Step)

### Step 5.1 - Open Cursor Settings

1. Open **Cursor**.
2. Press **Ctrl + ,** (Ctrl and comma) to open **Settings**.
   - Or click the gear icon in the bottom left corner and choose **Settings**.

### Step 5.2 - Open MCP Configuration

1. In the settings search bar, type **MCP** or **Model Context Protocol**.
2. Look for **"MCP Servers"** or **"Cursor > MCP: Servers"**.
3. Click **"Edit in settings.json"** to open the configuration file in JSON.
   - If this option doesn't appear, open manually: **File → Preferences → Open User Settings (JSON)** or use the command palette (**Ctrl + Shift + P**) and type **"Open User Settings (JSON)"**.

### Step 5.3 - Get the Full Path to `server.py`

1. In Windows File Explorer, navigate to the project folder:
   - `C:\path\to\local-llm-mcp-tool`
2. In the folder, locate the **`server.py`** file.
3. Hold **Shift**, right-click on **`server.py`** and choose **"Copy as path"**.
4. Paste into a notepad: the path will come with quotes. To use in JSON:
   - Remove the `"` quotes.
   - Replace each `\` with `\\` (double backslash).
   - Example: `C:\path\to\server.py` becomes `C:\\path\\to\\server.py`

**Example of path already formatted for JSON:**

```
C:\\path\\to\\local-llm-mcp-tool\\server.py
```

### Step 5.4 - Add MCP Server to `settings.json`

1. In the **settings.json** file you opened, check if a **`"mcpServers"`** key already exists.
2. **If `mcpServers` already exists:**
   - Inside `mcpServers`, add the **local-llm** block (see example below).
   - Pay attention to commas: after the last server there should be no comma.
3. **If `mcpServers` doesn't exist:**
   - Add the complete block below (adjusting the `server.py` path to yours).

**Complete example (copy and adjust the path in `args`):**

```json
{
  "mcpServers": {
    "local-llm": {
      "command": "python",
      "args": [
        "C:\\path\\to\\local-llm-mcp-tool\\server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

4. **Replace** the path in `args` with **your** full path to `server.py` (with `\\` instead of `\`).
5. Save the file (**Ctrl + S**).

### Step 5.5 - Restart Cursor

1. Close Cursor completely (all windows).
2. Open Cursor again.
3. Cursor will start the MCP server automatically when needed (you don't need to run `python server.py` manually to use it in Cursor).

### Step 5.6 - Verify the Server Appeared

1. In Cursor, open the **Chat** (assistant panel).
2. Look for **MCP**, **Tools**, or **Ferramentas** (depending on version).
3. The **"local-llm"** server should appear in the MCP servers list, with tools like **generate_text**, **chat**, and **complete**.

If you get a connection error or the server doesn't list tools:

- Check if the path in `args` is correct and has `\\`.
- Check if Python is in PATH (test in terminal: `python --version`).
- Check the MCP output in Cursor (usually in **Output** or **MCP** panel) for error messages.

### Step 5.7 - Use Tools in Chat

1. With the server configured and appearing in tools, you can ask in chat, for example:
   - *"Use the generate_text tool to generate a paragraph about Python."*
   - *"Call the chat tool from local-llm with the message: What is MCP?"*
2. Cursor will use your local Llama model (configured in your `.env`) to respond.

---

## Where to Test MCP in Cursor

### 1. Chat (Sidebar)

1. Open Cursor **Chat**:
   - Chat bubble icon in the left sidebar, or
   - **Ctrl + L** (common shortcut for Chat).
2. In the message field, type a request that uses your MCP, for example:
   - *"Use the generate_text tool from local-llm with prompt: Write a sentence about programming."*
   - *"Call the chat tool with message: What is Python?"*
   - *"Use the local-llm MCP to complete the text: Python is a language"*
3. Send the message. Cursor should call the **local-llm** server and show the response from your local model.

### 2. Composer (Agent Mode)

1. Open **Composer**:
   - Icon in the sidebar or **Ctrl + I** (depending on version).
2. In Composer you can request longer tasks; if the task needs text generation or chat, Cursor may use **local-llm** tools automatically when appropriate.

### 3. Check if MCP is Active

- **Settings:** **File → Preferences → Cursor Settings** (or **Ctrl + ,**) and search for **MCP** to see the list of servers.
- **Output:** **View → Output** and choose the **MCP** or **Cursor** panel to see connection logs and server errors.

### Example Phrases to Test in Chat

| What to Test | Example Message in Chat |
|--------------|-------------------------|
| generate_text | *"Use the generate_text tool from local-llm with prompt: What is artificial intelligence in one sentence."* |
| chat | *"Use the chat tool with messages: [{\"role\": \"user\", \"content\": \"Explain MCP in one sentence.\"}]"* |
| complete | *"Use the complete tool to complete: Python is a language"* |

If Cursor doesn't call the tool automatically, try being explicit: *"Use the [name] tool from the local-llm server..."*.

---

## Command Summary

| What to Do | Command / Action |
|------------|------------------|
| Install dependencies | `pip install -r requirements.txt` |
| Configure model | `copy .env.example .env` and edit `.env` |
| Download model | `python download_model.py` |
| Test | `python test_server.py` |
| Run server | `python server.py` or `python server_fastmcp.py` |
| Configure in Cursor | See section **5. Use with Cursor** above |
