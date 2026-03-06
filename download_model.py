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
    total_size = int(response.headers.get("content-length", 0))

    os.makedirs(os.path.dirname(destination), exist_ok=True)

    with open(destination, "wb") as file, tqdm(
        desc=os.path.basename(destination),
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                bar.update(len(chunk))


def list_hf_gguf_files(model_id: str):
    """Return list of .gguf files for a Hugging Face model id."""
    api_url = f"https://huggingface.co/api/models/{model_id}"
    try:
        response = requests.get(api_url, timeout=20)
        response.raise_for_status()
    except Exception as exc:
        print(f"\n✗ Failed to query Hugging Face API for '{model_id}': {exc}")
        return []

    try:
        data = response.json()
    except ValueError:
        print("\n✗ Unexpected response from Hugging Face API (not JSON).")
        return []

    siblings = data.get("siblings") or []
    gguf_files = [
        sibling.get("rfilename")
        for sibling in siblings
        if isinstance(sibling, dict)
        and isinstance(sibling.get("rfilename"), str)
        and sibling["rfilename"].endswith(".gguf")
    ]

    if not gguf_files:
        print(f"\n✗ No .gguf files found for model '{model_id}'.")

    return gguf_files


def search_hf_gguf_models(query: str, limit: int = 20):
    """Search Hugging Face for public, non-gated models that have GGUF files."""
    api_url = "https://huggingface.co/api/models"
    params = {"search": query, "limit": limit}
    try:
        response = requests.get(api_url, params=params, timeout=20)
        response.raise_for_status()
    except Exception as exc:
        print(f"\n✗ Failed to search Hugging Face for '{query}': {exc}")
        return []

    try:
        models = response.json()
    except ValueError:
        print("\n✗ Unexpected response from Hugging Face search API (not JSON).")
        return []

    results = []
    for model in models:
        # Skip private or gated models
        if model.get("private") or model.get("gated"):
            continue

        model_id = model.get("modelId") or model.get("id")
        if not isinstance(model_id, str):
            continue

        gguf_files = list_hf_gguf_files(model_id)
        if gguf_files:
            results.append({"id": model_id, "files": gguf_files})

    if not results:
        print(f"\n✗ No free GGUF models found for search '{query}'.")

    return results


def select_gguf_file_for_model(model_id: str, gguf_files):
    """Interactively choose a GGUF file from a model and build its download URL/filename."""
    if not gguf_files:
        return None, None

    if len(gguf_files) == 1:
        selected = gguf_files[0]
        print(f"\nUsing only available GGUF file: {selected}")
    else:
        print(f"\nAvailable GGUF files for model '{model_id}':")
        for idx, fname in enumerate(gguf_files, start=1):
            print(f"{idx}. {fname}")

        selection = input(
            f"Choose a file (1-{len(gguf_files)}, Enter for 1): "
        ).strip()
        if not selection:
            index = 1
        else:
            try:
                index = int(selection)
            except ValueError:
                print("Invalid selection!")
                return None, None

        if index < 1 or index > len(gguf_files):
            print("Selection out of range!")
            return None, None

        selected = gguf_files[index - 1]

    url = f"https://huggingface.co/{model_id}/resolve/main/{selected}"
    filename = Path(selected).name
    return url, filename


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
    print(
        "5. Hugging Face base name or model ID (auto-find free GGUF conversions, e.g. deepseek-ai/DeepSeek-Coder-V2-Lite-Base)"
    )
    print("6. Search free Hugging Face GGUF models by keyword")

    choice = input("\nChoose an option (1-6): ").strip()

    if choice in popular_models:
        url = popular_models[choice]["url"]
        filename = url.split("/")[-1]
    elif choice == "4":
        url = input("Enter the GGUF model URL: ").strip()
        filename = url.split("/")[-1]
    elif choice == "5":
        base_or_id = input(
            "Enter Hugging Face model ID or base name (e.g. deepseek-ai/DeepSeek-Coder-V2-Lite-Base): "
        ).strip()
        if not base_or_id:
            print("Model ID/base name cannot be empty!")
            return

        # First, try treating it as an exact model ID that already has GGUF files.
        model_id = base_or_id
        gguf_files = list_hf_gguf_files(model_id)

        # If that fails, search for public GGUF conversions by base name.
        if not gguf_files:
            base_name = base_or_id.split("/")[-1]
            print(
                f"\nNo GGUF files found directly in '{model_id}'. "
                f"Searching for free GGUF conversions of '{base_name}' on Hugging Face..."
            )
            matches = search_hf_gguf_models(base_name)
            if not matches:
                return

            print("\nMatching GGUF models:")
            for idx, match in enumerate(matches, start=1):
                print(f"{idx}. {match['id']} ({len(match['files'])} GGUF files)")

            selection = input(
                f"Choose a model (1-{len(matches)}, Enter for 1): "
            ).strip()
            if not selection:
                index = 1
            else:
                try:
                    index = int(selection)
                except ValueError:
                    print("Invalid selection!")
                    return

            if index < 1 or index > len(matches):
                print("Selection out of range!")
                return

            chosen = matches[index - 1]
            model_id = chosen["id"]
            gguf_files = chosen["files"]

        url, filename = select_gguf_file_for_model(model_id, gguf_files)
        if not url:
            return
    elif choice == "6":
        query = input(
            "Enter a search term for free GGUF models (e.g. 'llama-3.2-1b', 'deepseek-coder'): "
        ).strip()
        if not query:
            print("Search term cannot be empty!")
            return

        matches = search_hf_gguf_models(query)
        if not matches:
            return

        print("\nMatching GGUF models:")
        for idx, match in enumerate(matches, start=1):
            print(f"{idx}. {match['id']} ({len(match['files'])} GGUF files)")

        selection = input(
            f"Choose a model (1-{len(matches)}, Enter for 1): "
        ).strip()
        if not selection:
            index = 1
        else:
            try:
                index = int(selection)
            except ValueError:
                print("Invalid selection!")
                return

        if index < 1 or index > len(matches):
            print("Selection out of range!")
            return

        chosen = matches[index - 1]
        model_id = chosen["id"]
        gguf_files = chosen["files"]

        url, filename = select_gguf_file_for_model(model_id, gguf_files)
        if not url:
            return
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
