# Instalação no Windows - Guia Detalhado

## Problema Comum: Erro ao Instalar llama-cpp-python

Se você recebeu um erro como:
```
CMake Error: CMAKE_C_COMPILER not set
Failed building wheel for llama-cpp-python
```

Isso acontece porque `llama-cpp-python` precisa ser compilado, mas você não tem as ferramentas de compilação instaladas.

## Solução: Use Wheels Pré-Compilados

**NÃO** tente compilar do código fonte no Windows sem Visual Studio Build Tools. Use wheels pré-compilados!

### Passo 1: Instalar Dependências Básicas

```bash
pip install -r requirements.txt
```

### Passo 2: Instalar llama-cpp-python (Escolha uma opção)

#### Opção A: CPU (Mais Fácil - Recomendado)

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

#### Opção B: GPU NVIDIA (Melhor Performance)

Se você tem uma GPU NVIDIA com CUDA instalado:

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

Para outras versões de CUDA:
- CUDA 11.8: `--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118`
- CUDA 12.1: `--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121`
- CUDA 12.4: `--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124`

#### Opção C: Versão Específica (Se as outras falharem)

```bash
pip install llama-cpp-python==0.2.20 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### Passo 3: Verificar Instalação

```bash
python -c "from llama_cpp import Llama; print('✓ Instalado com sucesso!')"
```

## Alternativa: Instalar Compilador e Compilar do Código Fonte

Se os wheels pré-compilados não funcionarem no seu Windows, você pode instalar o compilador C/C++ e o CMake e compilar o pacote.

**Guia completo:** veja **[INSTALAR_COMPILADOR_WINDOWS.md](INSTALAR_COMPILADOR_WINDOWS.md)**.

Resumo rápido (Opção recomendada):

1. **Visual Studio Build Tools**:
   - Baixe: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Instale a carga **"Desenvolvimento para desktop com C++"**
   - Marque **"C++ CMake tools for Windows"**
   - Reinicie o terminal e execute: `pip install llama-cpp-python`

Isso resolve o erro de `nmake` e `CMAKE_C_COMPILER`.

## Troubleshooting

### Erro: "No module named 'llama_cpp'"
- Certifique-se de usar o `--extra-index-url` correto
- Tente desinstalar e reinstalar: `pip uninstall llama-cpp-python && pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`

### Erro: "Could not find a version"
- Verifique sua versão do Python (precisa ser 3.10+)
- Tente uma versão específica: `pip install llama-cpp-python==0.2.20 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`

### Performance Lenta
- Se tiver GPU NVIDIA, use a versão CUDA
- Configure `N_GPU_LAYERS` no `.env` para usar GPU
- Use modelos menores (1B-3B) para CPU

## Links Úteis

- Repositório oficial: https://github.com/abetlen/llama-cpp-python
- Wheels disponíveis: https://github.com/abetlen/llama-cpp-python/releases
- Documentação: https://llama-cpp-python.readthedocs.io/
