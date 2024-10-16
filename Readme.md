# MinhookStb

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/yurisizuku/win-MinhookStb?color=green&label=MinhookStb)![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/YuriSizuku/win-MinhookStb/build.yml?label=build)

🌿 A single header library (similar to [stb](https://github.com/nothings/stb)) for [minhook](https://github.com/TsudaKageyu/minhook),  
compatible with `gcc`, `tcc`, `llvm-mingw(clang)`, `msvc`.  

## usage

Include the single header file either in `src/stb_minhook.h` or `build/stb_minhook.h`, for example

```c
#define MINHOOK_IMPLEMENTATION
#ifndef MINHOOK_SHARED // if you want to build dll and export api
#include "std_minhook.h"
```

## build

prepare enviroment

```sh
git clone https://github.com/YuriSizuku/win-StbMinhook.git --recursive
cd win-StbMinhook
chmod +x script/*.sh script/*.py
export MINGWSDK=/path/to/llvmmingw && script/install_llvmmingw.sh
```

build stb_minhook.h

```sh
mkdir build
python script/build_stb_minhool.py
```

build for debug

```sh
make prepare stbminhook
make libminhook libminhook_test CC=i686-w64-mingw32-gcc BUILD_TYPE=32d
make libminhook libminhook_test CC=x86_64-w64-mingw32-gcc BUILD_TYPE=64d
```
