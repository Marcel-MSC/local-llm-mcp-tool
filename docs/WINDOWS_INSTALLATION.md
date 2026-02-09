# Windows Installation - Detailed Guide

## Common Problem: Error Installing llama-cpp-python

If you received an error like:
```
CMake Error: CMAKE_C_COMPILER not set
Failed building wheel for llama-cpp-python
```

This happens because `llama-cpp-python` needs to be compiled, but you don't have the compilation tools installed.

## Solution: Use Pre-Built Wheels

**DO NOT** try to compile from source on Windows without Visual Studio Build Tools. Use pre-built wheels!

### Step 1: Install Basic Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install llama-cpp-python (Choose an Option)

#### Option A: CPU (Easiest - Recommended)

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

#### Option B: NVIDIA GPU (Better Performance)

If you have an NVIDIA GPU with CUDA installed:

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

For other CUDA versions:
- CUDA 11.8: `--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118`
- CUDA 12.1: `--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121`
- CUDA 12.4: `--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124`

#### Option C: Specific Version (If Others Fail)

```bash
pip install llama-cpp-python==0.2.20 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### Step 3: Verify Installation

```bash
python -c "from llama_cpp import Llama; print('✓ Installed successfully!')"
```

## Alternative: Install Compiler and Compile from Source

If pre-built wheels don't work on your Windows, you can install the C/C++ compiler and CMake and compile the package.

**Complete guide:** see **[INSTALL_COMPILER_WINDOWS.md](INSTALL_COMPILER_WINDOWS.md)**.

Quick summary (Recommended option):

1. **Visual Studio Build Tools**:
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install the **"Desktop development with C++"** workload
   - Check **"C++ CMake tools for Windows"**
   - Restart terminal and run: `pip install llama-cpp-python`

This resolves the `nmake` and `CMAKE_C_COMPILER` error.

## Troubleshooting

### Error: "No module named 'llama_cpp'"
- Make sure to use the correct `--extra-index-url`
- Try uninstalling and reinstalling: `pip uninstall llama-cpp-python && pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`

### Error: "Could not find a version"
- Check your Python version (needs to be 3.10+)
- Try a specific version: `pip install llama-cpp-python==0.2.20 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`

### Slow Performance
- If you have NVIDIA GPU, use the CUDA version
- Configure `N_GPU_LAYERS` in `.env` to use GPU
- Use smaller models (1B-3B) for CPU

## Useful Links

- Official repository: https://github.com/abetlen/llama-cpp-python
- Available wheels: https://github.com/abetlen/llama-cpp-python/releases
- Documentation: https://llama-cpp-python.readthedocs.io/
