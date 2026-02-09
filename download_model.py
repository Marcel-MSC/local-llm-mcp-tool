"""
Script helper para baixar modelos Llama GGUF
"""
import os
import sys
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url: str, destination: str):
    """Baixa um arquivo com barra de progresso"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    with open(destination, 'wb') as file, tqdm(
        desc=os.path.basename(destination),
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                bar.update(len(chunk))

def main():
    """Menu interativo para baixar modelos"""
    print("=== Download de Modelos Llama GGUF ===\n")
    
    modelos_populares = {
        "1": {
            "nome": "Llama 3.2 1B (leve, recomendado para CPU)",
            "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
        },
        "2": {
            "nome": "Llama 3.1 8B (balanceado)",
            "url": "https://huggingface.co/bartowski/Llama-3.1-8B-Instruct-GGUF/resolve/main/Llama-3.1-8B-Instruct-Q4_K_M.gguf"
        },
        "3": {
            "nome": "Mistral 7B (alternativa)",
            "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        }
    }
    
    print("Modelos disponíveis:")
    for key, modelo in modelos_populares.items():
        print(f"{key}. {modelo['nome']}")
    print("4. URL personalizada")
    
    escolha = input("\nEscolha uma opção (1-4): ").strip()
    
    if escolha in modelos_populares:
        url = modelos_populares[escolha]["url"]
        nome_arquivo = url.split("/")[-1]
    elif escolha == "4":
        url = input("Digite a URL do modelo GGUF: ").strip()
        nome_arquivo = url.split("/")[-1]
    else:
        print("Opção inválida!")
        return
    
    # Pede o diretório de destino
    default_dir = "models"
    destino_dir = input(f"Diretório de destino (Enter para '{default_dir}'): ").strip() or default_dir
    destino = os.path.join(destino_dir, nome_arquivo)
    
    print(f"\nBaixando para: {destino}")
    print("Isso pode levar alguns minutos...\n")
    
    try:
        download_file(url, destino)
        print(f"\n✓ Modelo baixado com sucesso!")
        print(f"\nConfigure no arquivo .env:")
        print(f"MODEL_PATH={os.path.abspath(destino)}")
    except Exception as e:
        print(f"\n✗ Erro ao baixar: {e}")

if __name__ == "__main__":
    try:
        import requests
        from tqdm import tqdm
    except ImportError:
        print("Instalando dependências necessárias...")
        os.system("pip install requests tqdm")
        import requests
        from tqdm import tqdm
    
    main()
