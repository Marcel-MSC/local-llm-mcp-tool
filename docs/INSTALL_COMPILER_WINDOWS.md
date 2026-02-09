# How to Install C/C++ Compiler and CMake on Windows

Yes, installing the C compiler and CMake **solves the problem** with `llama-cpp-python`. After that, you can use:

```bash
pip install llama-cpp-python
```

without needing pre-built wheels.

---

## Option 1: Visual Studio Build Tools (Recommended)

This is the most complete and official way for Windows.

### Step 1: Download the Installer

1. Visit: **https://visualstudio.microsoft.com/visual-cpp-build-tools/**
2. Click **"Download Build Tools"**
3. Run the downloaded `vs_BuildTools.exe` file

### Step 2: Choose Components

1. In the installer, check the workload:
   - **"Desktop development with C++"**
2. In the right panel, make sure these are checked:
   - **MSVC** (Microsoft compiler)
   - **Windows 10/11 SDK**
   - **C++ CMake tools for Windows** (CMake)
3. Click **"Install"** (may take 10-30 minutes and several GB)

### Step 3: Restart and Use

1. Close and reopen the terminal (CMD or PowerShell).
2. Install the package:

```bash
pip install llama-cpp-python
```

pip will use the installed compiler and CMake and compile the package.

---

## Option 2: CMake Only (Not Enough Alone)

The error also mentions **nmake** and **CMAKE_C_COMPILER**. So you need:

- **CMake** - to generate the project
- **C/C++ Compiler** - e.g., **MSVC** (Visual Studio) or **MinGW**

Installing only CMake **doesn't solve it**: you need a compiler (like the one that comes with Option 1).

---

## Option 3: MinGW (Lighter Alternative)

If you don't want to install Visual Studio Build Tools, you can use MinGW:

### 1. Download w64devkit

1. Visit: **https://github.com/skeeto/w64devkit/releases**
2. Download **w64devkit-x.x.x.zip** (latest version)
3. Extract to a folder, e.g.: `C:\w64devkit`

### 2. Add to PATH

1. Open **Settings** → **System** → **About** → **Advanced system settings**
2. Click **Environment Variables**
3. Under **System variables**, edit **Path** and add:
   - `C:\w64devkit\bin` (adjust if extracted elsewhere)

### 3. Install CMake

1. Visit: **https://cmake.org/download/**
2. Download **Windows x64 Installer**
3. Install and check **"Add CMake to the system PATH"**

### 4. Install llama-cpp-python with MinGW

Open a **new** PowerShell and run:

```powershell
$env:CMAKE_GENERATOR = "MinGW Makefiles"
$env:CMAKE_ARGS = "-DCMAKE_C_COMPILER=C:/w64devkit/bin/gcc.exe -DCMAKE_CXX_COMPILER=C:/w64devkit/bin/g++.exe"
pip install llama-cpp-python
```

Adjust the `C:/w64devkit` path if extracted elsewhere.

---

## Summary

| Option | Difficulty | Size | Recommendation |
|--------|------------|------|----------------|
| **1. Visual Studio Build Tools** | Medium | ~7 GB | **Best option**: everything in one installer |
| **2. CMake Only** | Easy | Small | **Doesn't solve** alone (missing compiler) |
| **3. MinGW + CMake** | Medium | ~100 MB | Lighter alternative |

After installing **Option 1** (or 3 correctly), use:

```bash
pip install llama-cpp-python
```

and the compilation error should disappear.

---

## Verify It Worked

After installing the tools and the package:

```bash
python -c "from llama_cpp import Llama; print('OK!')"
```

If it shows `OK!`, the installation is correct.
