"""
Quick test script to verify if the MCP server is working
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_model_loading():
    """Tests if the model can be loaded"""
    print("=== Test: Model Loading ===\n")
    
    model_path = os.getenv("MODEL_PATH", "")
    
    if not model_path:
        print("❌ MODEL_PATH is not configured in .env file")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Configure MODEL_PATH with the path to a .gguf file")
        print("3. Or run: python download_model.py")
        return False
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return False
    
    print(f"✓ File found: {model_path}")
    print(f"  Size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
    
    try:
        from llama_cpp import Llama
        print("\nLoading model...")
        
        model = Llama(
            model_path=model_path,
            n_ctx=512,  # Smaller context for quick test
            n_threads=2,
            verbose=False
        )
        
        print("✓ Model loaded successfully!")
        
        # Quick generation test
        print("\nTesting text generation...")
        output = model("Hello", max_tokens=10, temperature=0.7, echo=False)
        print(f"✓ Model response: {output['choices'][0]['text']}")
        
        return True
        
    except ImportError:
        print("❌ llama-cpp-python is not installed")
        print("Install with: pip install llama-cpp-python")
        return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False


def test_mcp_imports():
    """Tests if MCP dependencies are installed"""
    print("\n=== Test: MCP Dependencies ===\n")
    
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
        print("✓ MCP libraries imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Error importing MCP libraries: {e}")
        print("Install with: pip install mcp")
        return False


def main():
    """Runs all tests"""
    print("Testing Local LLM MCP server configuration\n")
    print("=" * 50)
    
    mcp_ok = test_mcp_imports()
    model_ok = test_model_loading()
    
    print("\n" + "=" * 50)
    print("\nSummary:")
    print(f"  MCP: {'✓ OK' if mcp_ok else '❌ FAILED'}")
    print(f"  Model: {'✓ OK' if model_ok else '❌ FAILED'}")
    
    if mcp_ok and model_ok:
        print("\n✅ All ready! You can run the server with:")
        print("   python server.py")
    else:
        print("\n⚠️  Fix the issues above before running the server")


if __name__ == "__main__":
    main()
