"""
Helper script to download Llama GGUF models
"""
import os
import sys
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url: str, destination: str):
    """Downloads a file with progress bar"""
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
    """Interactive menu to download models"""
    print("=== Download Llama GGUF Models ===\n")
    
    popular_models = {
        "1": {
            "name": "Llama 3.2 1B (lightweight, recommended for CPU)",
            "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
        },
        "2": {
            "name": "Llama 3.1 8B (balanced)",
            "url": "https://huggingface.co/bartowski/Llama-3.1-8B-Instruct-GGUF/resolve/main/Llama-3.1-8B-Instruct-Q4_K_M.gguf"
        },
        "3": {
            "name": "Mistral 7B (alternative)",
            "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        }
    }
    
    print("Available models:")
    for key, model in popular_models.items():
        print(f"{key}. {model['name']}")
    print("4. Custom URL")
    
    choice = input("\nChoose an option (1-4): ").strip()
    
    if choice in popular_models:
        url = popular_models[choice]["url"]
        filename = url.split("/")[-1]
    elif choice == "4":
        url = input("Enter the GGUF model URL: ").strip()
        filename = url.split("/")[-1]
    else:
        print("Invalid option!")
        return
    
    # Ask for destination directory
    default_dir = "models"
    dest_dir = input(f"Destination directory (Enter for '{default_dir}'): ").strip() or default_dir
    destination = os.path.join(dest_dir, filename)
    
    print(f"\nDownloading to: {destination}")
    print("This may take a few minutes...\n")
    
    try:
        download_file(url, destination)
        print(f"\n✓ Model downloaded successfully!")
        print(f"\nConfigure in .env file:")
        print(f"MODEL_PATH={os.path.abspath(destination)}")
    except Exception as e:
        print(f"\n✗ Error downloading: {e}")

if __name__ == "__main__":
    try:
        import requests
        from tqdm import tqdm
    except ImportError:
        print("Installing required dependencies...")
        os.system("pip install requests tqdm")
        import requests
        from tqdm import tqdm
    
    main()
