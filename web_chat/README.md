# Local LLM Web Chat

Interface web para enviar mensagens, arquivos e ver métricas do modelo local.

## Instalação

Na raiz do projeto:

```bash
pip install -r web_chat/requirements.txt
```

## Executar

Na raiz do projeto (para que o `server` seja encontrado):

```bash
uvicorn web_chat.app:app --reload --host 0.0.0.0 --port 8000
```

Ou:

```bash
cd web_chat && python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

(Na segunda opção, pode ser necessário ajustar o `sys.path` se o `server` não for encontrado.)

Acesse: http://localhost:8000

## Funcionalidades

- **Chat**: Enviar mensagens e receber respostas do modelo local
- **Arquivos**: Anexar arquivos e analisar com o modelo
- **Config**: Ver modelo em uso e parâmetros (contexto, threads, GPU)
- **Dashboard**: Tokens usados, tempo de resposta, requisições recentes

## Requisitos

- `MODEL_PATH` configurado no `.env` na raiz do projeto
- `llama-cpp-python` instalado (via `install_llama.ps1` ou `pip`)
