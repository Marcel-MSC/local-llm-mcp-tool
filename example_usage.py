"""
Exemplo de uso do servidor MCP Llama localmente
Este arquivo demonstra como usar o servidor programaticamente
"""
import asyncio
from server import load_model, llama_model

async def exemplo_geracao_texto():
    """Exemplo de geração de texto"""
    print("=== Exemplo: Geração de Texto ===")
    
    model = load_model()
    
    prompt = "Escreva uma história curta sobre um robô que aprende a cozinhar."
    print(f"Prompt: {prompt}\n")
    
    output = model(
        prompt,
        max_tokens=200,
        temperature=0.7,
        top_p=0.9,
        echo=False
    )
    
    print("Resposta:")
    print(output["choices"][0]["text"])
    print()


async def exemplo_chat():
    """Exemplo de chat"""
    print("=== Exemplo: Chat ===")
    
    model = load_model()
    
    messages = [
        {"role": "system", "content": "Você é um assistente útil e amigável."},
        {"role": "user", "content": "Explique o que é inteligência artificial em uma frase."}
    ]
    
    # Converte para prompt
    prompt_parts = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
    
    prompt = "\n".join(prompt_parts) + "\nAssistant:"
    
    output = model(
        prompt,
        max_tokens=150,
        temperature=0.7,
        echo=False,
        stop=["User:", "System:"]
    )
    
    print("Resposta do assistente:")
    print(output["choices"][0]["text"].strip())
    print()


async def exemplo_completar():
    """Exemplo de completar texto"""
    print("=== Exemplo: Completar Texto ===")
    
    model = load_model()
    
    text = "Python é uma linguagem de programação"
    print(f"Texto inicial: {text}\n")
    
    output = model(
        text,
        max_tokens=100,
        temperature=0.7,
        echo=False
    )
    
    print("Texto completo:")
    print(output["choices"][0]["text"])
    print()


async def main():
    """Executa todos os exemplos"""
    try:
        await exemplo_geracao_texto()
        await exemplo_chat()
        await exemplo_completar()
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        print("\nPor favor:")
        print("1. Configure MODEL_PATH no arquivo .env")
        print("2. Baixe um modelo GGUF de https://huggingface.co/models?library=gguf")
    except Exception as e:
        print(f"Erro ao executar exemplos: {e}")


if __name__ == "__main__":
    asyncio.run(main())
