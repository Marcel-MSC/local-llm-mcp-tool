# Como Instalar o Compilador C/C++ e CMake no Windows

Sim, instalar o compilador C e o CMake **resolve o problema** do `llama-cpp-python`. Depois disso, você pode usar:

```bash
pip install llama-cpp-python
```

sem precisar de wheels pré-compilados.

---

## Opção 1: Visual Studio Build Tools (Recomendado)

Esta é a forma mais completa e oficial para Windows.

### Passo 1: Baixar o instalador

1. Acesse: **https://visualstudio.microsoft.com/visual-cpp-build-tools/**
2. Clique em **"Baixar Build Tools"**
3. Execute o arquivo `vs_BuildTools.exe` baixado

### Passo 2: Escolher os componentes

1. No instalador, marque a carga de trabalho:
   - **"Desenvolvimento para desktop com C++"** (Desktop development with C++)
2. No painel à direita, confira se estão marcados:
   - **MSVC** (compilador da Microsoft)
   - **Windows 10/11 SDK**
   - **C++ CMake tools for Windows** (CMake)
3. Clique em **"Instalar"** (pode levar 10–30 minutos e vários GB)

### Passo 3: Reiniciar e usar

1. Feche e abra de novo o terminal (CMD ou PowerShell).
2. Instale o pacote:

```bash
pip install llama-cpp-python
```

O pip usará o compilador e o CMake instalados e compilará o pacote.

---

## Opção 2: Apenas CMake (não basta sozinho)

O erro também fala de **nmake** e **CMAKE_C_COMPILER**. Ou seja, você precisa de:

- **CMake** – para gerar o projeto
- **Compilador C/C++** – por exemplo **MSVC** (Visual Studio) ou **MinGW**

Instalar só o CMake **não resolve**: é preciso ter um compilador (como o que vem com a Opção 1).

---

## Opção 3: MinGW (alternativa mais leve)

Se não quiser instalar o Visual Studio Build Tools, pode usar o MinGW:

### 1. Baixar o w64devkit

1. Acesse: **https://github.com/skeeto/w64devkit/releases**
2. Baixe **w64devkit-x.x.x.zip** (versão mais recente)
3. Extraia em uma pasta, por exemplo: `C:\w64devkit`

### 2. Adicionar ao PATH

1. Abra **Configurações** → **Sistema** → **Sobre** → **Configurações avançadas do sistema**
2. Clique em **Variáveis de ambiente**
3. Em **Variáveis do sistema**, edite **Path** e adicione:
   - `C:\w64devkit\bin` (ajuste se tiver extraído em outro lugar)

### 3. Instalar o CMake

1. Acesse: **https://cmake.org/download/**
2. Baixe **Windows x64 Installer**
3. Instale e marque **"Add CMake to the system PATH"**

### 4. Instalar o llama-cpp-python com MinGW

Abra um **novo** PowerShell e execute:

```powershell
$env:CMAKE_GENERATOR = "MinGW Makefiles"
$env:CMAKE_ARGS = "-DCMAKE_C_COMPILER=C:/w64devkit/bin/gcc.exe -DCMAKE_CXX_COMPILER=C:/w64devkit/bin/g++.exe"
pip install llama-cpp-python
```

Ajuste o caminho `C:/w64devkit` se tiver extraído em outra pasta.

---

## Resumo

| Opção | Dificuldade | Tamanho | Recomendação |
|-------|-------------|---------|--------------|
| **1. Visual Studio Build Tools** | Média | ~7 GB | **Melhor opção**: tudo em um instalador |
| **2. Só CMake** | Fácil | Pequeno | **Não resolve** sozinho (falta compilador) |
| **3. MinGW + CMake** | Média | ~100 MB | Alternativa mais leve |

Depois de instalar a **Opção 1** (ou a 3 corretamente), use:

```bash
pip install llama-cpp-python
```

e o erro de compilação deve desaparecer.

---

## Verificar se deu certo

Depois de instalar as ferramentas e o pacote:

```bash
python -c "from llama_cpp import Llama; print('OK!')"
```

Se aparecer `OK!`, a instalação está correta.
