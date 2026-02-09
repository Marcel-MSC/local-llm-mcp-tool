"""
Example usage of the local Llama MCP server
This file demonstrates how to use the server programmatically
"""
import asyncio
from server import load_model, llama_model

async def example_text_generation():
    """Example of text generation"""
    print("=== Example: Text Generation ===")
    
    model = load_model()
    
    prompt = "Write a short story about a robot that learns to cook."
    print(f"Prompt: {prompt}\n")
    
    output = model(
        prompt,
        max_tokens=200,
        temperature=0.7,
        top_p=0.9,
        echo=False
    )
    
    print("Response:")
    print(output["choices"][0]["text"])
    print()


async def example_chat():
    """Example of chat"""
    print("=== Example: Chat ===")
    
    model = load_model()
    
    messages = [
        {"role": "system", "content": "You are a helpful and friendly assistant."},
        {"role": "user", "content": "Explain what artificial intelligence is in one sentence."}
    ]
    
    # Convert to prompt
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
    
    print("Assistant response:")
    print(output["choices"][0]["text"].strip())
    print()


async def example_complete():
    """Example of text completion"""
    print("=== Example: Text Completion ===")
    
    model = load_model()
    
    text = "Python is a programming language"
    print(f"Initial text: {text}\n")
    
    output = model(
        text,
        max_tokens=100,
        temperature=0.7,
        echo=False
    )
    
    print("Completed text:")
    print(output["choices"][0]["text"])
    print()


async def main():
    """Runs all examples"""
    try:
        await example_text_generation()
        await example_chat()
        await example_complete()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease:")
        print("1. Configure MODEL_PATH in the .env file")
        print("2. Download a GGUF model from https://huggingface.co/models?library=gguf")
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())
