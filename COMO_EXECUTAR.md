# Como Executar o Aplicativo

## 1. Instalar as dependências do projeto

Sim, você deve instalar o que está no `requirements.txt`. O `llama-cpp-python` você já instalou; o comando abaixo instala o resto (MCP, pydantic, python-dotenv, etc.):

```bash
cd local-llm-mcp-tool
pip install -r requirements.txt
```

O pip vai instalar apenas o que faltar; o que já estiver instalado será mantido.

---

## 2. Configurar o modelo

Se ainda não tiver um modelo GGUF:

```bash
copy .env.example .env
```

Edite o arquivo `.env` e defina o caminho do seu modelo:

```
MODEL_PATH=C:\caminho\para\seu\modelo.gguf
```

Se não tiver um modelo, baixe um:

```bash
python download_model.py
```

Depois, no `.env`, coloque o caminho do arquivo que foi baixado (por exemplo `models\NomeDoModelo.gguf`).

---

## 3. Testar (opcional)

```bash
python test_server.py
```

Se aparecer "Tudo pronto!", pode seguir para o próximo passo.

---

## 4. Executar o servidor MCP

**Opção A – Servidor padrão:**

```bash
python server.py
```

**Opção B – Servidor FastMCP (mais simples):**

```bash
python server_fastmcp.py
```

O servidor ficará rodando e aguardando conexões (por exemplo do Cursor). Para parar: `Ctrl+C`.

---

## 5. Usar no Cursor (passo a passo)

### Passo 5.1 – Abrir as configurações do Cursor

1. Abra o **Cursor**.
2. Pressione **Ctrl + ,** (Ctrl e vírgula) para abrir **Settings** (Configurações).
   - Ou clique no ícone de engrenagem no canto inferior esquerdo e escolha **Settings**.

### Passo 5.2 – Abrir a configuração de MCP

1. Na barra de busca das configurações, digite **MCP** ou **Model Context Protocol**.
2. Procure por **"MCP Servers"** ou **"Cursor > MCP: Servers"**.
3. Clique em **"Edit in settings.json"** (Editar em settings.json) para abrir o arquivo de configuração em JSON.
   - Se não aparecer essa opção, abra manualmente: **File → Preferences → Open User Settings (JSON)** ou use a paleta de comandos (**Ctrl + Shift + P**) e digite **"Open User Settings (JSON)"**.

### Passo 5.3 – Obter o caminho completo do `server.py`

1. No Explorador de Arquivos do Windows, vá até a pasta do projeto:
   - `C:\path\to\local-llm-mcp-tool`
2. Na pasta, localize o arquivo **`server.py`**.
3. Segure **Shift**, clique com o botão direito em **`server.py`** e escolha **"Copiar como caminho"**.
4. Cole em um bloco de notas: o caminho virá entre aspas. Para usar no JSON:
   - Troque `"` por nada (remova as aspas).
   - Troque cada `\` por `\\` (barra invertida dupla).
   - Exemplo: `C:\path\to\server.py` vira `C:\\path\\to\\server.py`

**Exemplo de caminho já formatado para o JSON:**

```
C:\\path\\to\\local-llm-mcp-tool\\server.py
```

### Passo 5.4 – Adicionar o servidor MCP no `settings.json`

1. No arquivo **settings.json** que abriu, procure se já existe uma chave **`"mcpServers"`**.
2. **Se já existir `mcpServers`:**
   - Dentro de `mcpServers`, adicione o bloco do **local-llm** (veja o exemplo abaixo).
   - Preste atenção nas vírgulas: depois do último servidor não deve ter vírgula.
3. **Se não existir `mcpServers`:**
   - Adicione o bloco completo abaixo (ajustando o caminho do `server.py` para o seu).

**Exemplo completo (copie e ajuste o caminho em `args`):**

```json
{
  "mcpServers": {
    "personal-llama": {
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

4. **Substitua** o caminho em `args` pelo **seu** caminho completo do `server.py` (com `\\` no lugar de `\`).
5. Salve o arquivo (**Ctrl + S**).

### Passo 5.5 – Reiniciar o Cursor

1. Feche o Cursor completamente (todas as janelas).
2. Abra o Cursor de novo.
3. O Cursor vai iniciar o servidor MCP automaticamente quando precisar (não é necessário rodar `python server.py` manualmente para usar no Cursor).

### Passo 5.6 – Verificar se o servidor apareceu

1. No Cursor, abra o **Chat** (painel do assistente).
2. Procure por **MCP**, **Tools** ou **Ferramentas** (dependendo da versão).
3. O servidor **"personal-llama"** deve aparecer na lista de servidores MCP, com ferramentas como **generate_text**, **chat** e **complete**.

Se aparecer erro de conexão ou o servidor não listar as ferramentas:

- Confira se o caminho em `args` está correto e com `\\`.
- Confira se o Python está no PATH (teste no terminal: `python --version`).
- Veja a saída do MCP no Cursor (geralmente em **Output** ou **MCP**) para mensagens de erro.

### Passo 5.7 – Usar as ferramentas no chat

1. Com o servidor configurado e aparecendo nas ferramentas, você pode pedir no chat, por exemplo:
   - *"Use a ferramenta generate_text para gerar um parágrafo sobre Python."*
   - *"Chame a ferramenta chat do personal-llama com a mensagem: O que é MCP?"*
2. O Cursor usará o modelo Llama local (configurado no seu `.env`) para responder.

---

## Onde testar o MCP no Cursor

### 1. Chat (lateral)

1. Abra o **Chat** do Cursor:
   - Ícone de balão de conversa na barra lateral esquerda, ou
   - **Ctrl + L** (atalho comum para o Chat).
2. No campo de mensagem, digite um pedido que use o seu MCP, por exemplo:
   - *"Use a ferramenta generate_text do personal-llama com o prompt: Escreva uma frase sobre programação."*
   - *"Chame a ferramenta chat com a mensagem: O que é Python?"*
   - *"Use o MCP personal-llama para completar o texto: Python é uma linguagem"*
3. Envie a mensagem. O Cursor deve chamar o servidor **personal-llama** e mostrar a resposta do seu modelo local.

### 2. Composer (modo agente)

1. Abra o **Composer**:
   - Ícone na barra lateral ou **Ctrl + I** (dependendo da versão).
2. No Composer você pode pedir tarefas mais longas; se a tarefa precisar de geração de texto ou chat, o Cursor pode usar as ferramentas do **personal-llama** automaticamente quando fizer sentido.

### 3. Ver se o MCP está ativo

- **Configurações:** **File → Preferences → Cursor Settings** (ou **Ctrl + ,**) e procure por **MCP** para ver a lista de servidores.
- **Output:** **View → Output** e escolha o painel **MCP** ou **Cursor** para ver logs de conexão e erros do servidor.

### Exemplos de frases para testar no Chat

| O que testar   | Exemplo de mensagem no Chat |
|----------------|-----------------------------|
| generate_text  | *"Use a ferramenta generate_text do personal-llama com prompt: O que é inteligência artificial em uma frase."* |
| chat           | *"Use a ferramenta chat com messages: [{\"role\": \"user\", \"content\": \"Explique MCP em uma frase.\"}]"* |
| complete       | *"Use a ferramenta complete para completar: Python é uma linguagem"* |

Se o Cursor não chamar a ferramenta sozinho, tente ser explícito: *"Use a ferramenta [nome] do servidor personal-llama..."*.

---

## Resumo dos comandos

| O que fazer              | Comando / Ação                          |
|--------------------------|-----------------------------------------|
| Instalar dependências    | `pip install -r requirements.txt`       |
| Configurar modelo        | `copy .env.example .env` e editar `.env`|
| Baixar modelo            | `python download_model.py`              |
| Testar                   | `python test_server.py`                 |
| Executar servidor        | `python server.py` ou `python server_fastmcp.py` |
| Configurar no Cursor     | Ver seção **5. Usar no Cursor** acima   |
