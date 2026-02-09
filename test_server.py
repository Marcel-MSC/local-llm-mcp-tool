"""
Script de teste rápido para verificar se o servidor MCP está funcionando
"""
import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_model_loading():
    """Testa se o modelo pode ser carregado"""
    print("=== Teste: Carregamento do Modelo ===\n")
    
    model_path = os.getenv("MODEL_PATH", "")
    
    if not model_path:
        print("❌ MODEL_PATH não está configurado no arquivo .env")
        print("\nPor favor:")
        print("1. Copie .env.example para .env")
        print("2. Configure MODEL_PATH com o caminho para um arquivo .gguf")
        print("3. Ou execute: python download_model.py")
        return False
    
    if not os.path.exists(model_path):
        print(f"❌ Arquivo do modelo não encontrado: {model_path}")
        return False
    
    print(f"✓ Arquivo encontrado: {model_path}")
    print(f"  Tamanho: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
    
    try:
        from llama_cpp import Llama
        print("\nCarregando modelo...")
        
        model = Llama(
            model_path=model_path,
            n_ctx=512,  # Contexto menor para teste rápido
            n_threads=2,
            verbose=False
        )
        
        print("✓ Modelo carregado com sucesso!")
        
        # Teste rápido de geração
        print("\nTestando geração de texto...")
        output = model("Olá", max_tokens=10, temperature=0.7, echo=False)
        print(f"✓ Resposta do modelo: {output['choices'][0]['text']}")
        
        return True
        
    except ImportError:
        print("❌ llama-cpp-python não está instalado")
        print("Instale com: pip install llama-cpp-python")
        return False
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return False


def test_mcp_imports():
    """Testa se as dependências MCP estão instaladas"""
    print("\n=== Teste: Dependências MCP ===\n")
    
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
        print("✓ Bibliotecas MCP importadas com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar bibliotecas MCP: {e}")
        print("Instale com: pip install mcp")
        return False


def main():
    """Executa todos os testes"""
    print("Testando configuração do servidor MCP Llama\n")
    print("=" * 50)
    
    mcp_ok = test_mcp_imports()
    model_ok = test_model_loading()
    
    print("\n" + "=" * 50)
    print("\nResumo:")
    print(f"  MCP: {'✓ OK' if mcp_ok else '❌ FALHOU'}")
    print(f"  Modelo: {'✓ OK' if model_ok else '❌ FALHOU'}")
    
    if mcp_ok and model_ok:
        print("\n✅ Tudo pronto! Você pode executar o servidor com:")
        print("   python server.py")
    else:
        print("\n⚠️  Corrija os problemas acima antes de executar o servidor")


if __name__ == "__main__":
    main()
