# stb minhook

A single header library of [minhook](https://github.com/TsudaKageyu/minhook)  , compatible with `gcc`, `tcc`, `llvm-mingw(clang)`.  
The namestyle is mostly like [stb](https://github.com/nothings/stb) style.

## build

prepare enviroment

```sh
git clone https://github.com/YuriSizuku/win-StbMinhook.git --recursive
cd win-StbMinhook
chmod +x script/*.sh script/*.py
export MINGWSDK=/path/to/llvm-mingw && script/install_llvm-mingw.sh
```

build stb_minhook.h

```sh
mkdir dist
python script/build_stb_minhool.py
```

build for testing

```sh
make stbminhook
make libminhook libminhook_test CC=i686-w64-mingw32-gcc BUILD_TYPE=32d
make libminhook libminhook_test CC=x86_64-w64-mingw32-gcc BUILD_TYPE=64d
```

## usage

Include the single header file either in `src/stb_minhook.h` or `dist/stb_minhook.h`, for example

```c
#define MINHOOK_IMPLEMENTATION
#ifndef MINHOOK_SHARED // if you want to build dll and export api
#include "std_minhook.h"
```
