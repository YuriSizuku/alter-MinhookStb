"""
generate stb_minhook.h file
    v0.1, developed by devseed
"""

info = \
"""// single header file composed by devseed
// see https://github.com/YuriSizuku/alter-MinhookStb
"""

import re
import os
import sys

# general function
def mark_section(info):
    def wrapper1(func): # decorator(dec_args)(func)(fun_args)
        def wrapper2(*args, **kw):
            ccode = func(*args, **kw)
            return f"#if 1 // {info}\n{ccode}\n#endif"
        return wrapper2
    return wrapper1

def ccode_replace(pattern, repl, count=0, flags=0):
    def wrapper1(func): # decorator(dec_args)(func)(fun_args)
        def wrapper2(*args, **kw):
            ccode = func(*args, **kw)
            return re.sub(pattern, repl, ccode, count=count, flags=flags)
        return wrapper2
    return wrapper1

def read_lines(inpath, encoding="utf-8"):
    with open(inpath, "r", encoding=encoding) as fp:
        lines = fp.readlines()
    return lines

def replace_lines(lines, replace_map, strip_left=False):
    for i, line in enumerate(lines):
        for k, v in replace_map.items():
            if line.find(k) >=0: 
                lines[i] = line.replace(k, v)
                if strip_left: lines[i] = lines[i].lstrip()
    return lines

def static_func(lines):
    for i, line in enumerate(lines):
        if re.match(r"\w(.+?)\s*(.+?)\((.+?)\)\s*;", line.lstrip()):
            lines[i] = "static " + line
    return lines

# stb function
def make_stbdecl() -> str:
    return  r"""
#if defined(_MSC_VER) || defined(__TINYC__)
#ifndef EXPORT
#define EXPORT __declspec(dllexport)
#endif
#else
#ifndef EXPORT 
#define EXPORT __attribute__((visibility("default")))
#endif
#endif // _MSC_VER
#ifndef MINHOOK_API
#ifdef MINHOOK_STATIC
#define MINHOOK_API_DEF static
#else
#define MINHOOK_API_DEF extern
#endif // MINHOOK_STATIC
#ifdef MINHOOK_SHARED
#define MINHOOK_API_EXPORT EXPORT
#else  
#define MINHOOK_API_EXPORT
#endif // MINHOOK_SHARED
#define MINHOOK_API MINHOOK_API_DEF MINHOOK_API_EXPORT
#endif // MINHOOK_API

#ifndef LOGi
#define LOGi(format, ...) {\
    printf("[%s,%s] ", __func__, "I");\
    printf(format, ##__VA_ARGS__);}
#endif

#define MINHOOK_DEFINE(name) \
    static T_##name name##_org = NULL; \
    static void *name##_old; \
    static HANDLE name##_mutex = NULL;

#define MINHOOK_BINDEXP(dll, name) \
    name##_old = (T_##name)GetProcAddress(dll, #name); \
    if(name##_old) { \
        MH_CreateHook(name##_old, (LPVOID)(name##_hook), (LPVOID*)(&name##_org)); \
        LOGi("MINHOOK_BIND " #name " %p -> %p\n", name##_old, name##_hook); \
        MH_EnableHook(name##_old); \
        name##_mutex = CreateMutex(NULL, FALSE, NULL); \
    }

#define MINHOOK_BINDADDR(addr, name) \
    name##_old = addr; \
    if(name##_old) { \
        MH_CreateHook(name##_old, (LPVOID)(name##_hook), (LPVOID*)(&name##_org)); \
        LOGi("MINHOOK_BIND " #name " %p -> %p\n", name##_old, name##_hook); \
        MH_EnableHook(name##_old); \
        name##_mutex = CreateMutex(NULL, FALSE, NULL); \
    }

#define MINHOOK_UNBIND(name) \
    if(name##_old) {\
        MH_RemoveHook(name##_old); \
        CloseHandle(name##_mutex); \
        LOGi("MINHOOK_UNBIND " #name " %p\n", name##_old); \
    }

#define MINHOOK_ENABLE(name) \
    LOGi("MINHOOK_ENABLE " #name " %p\n", name##_old); \
    MH_EnableHook(name##_old);

#define MINHOOK_DISABLE(name) \
    LOGi("MINHOOK_DISABLE " #name " %p\n", name##_old); \
    MH_DisableHook(name##_old);

#define MINHOOK_ENTERFUNC(name) \
    WaitForSingleObject(name##_mutex, INFINITE); \
    T_##name pfn = name##_org;

#define MINHOOK_LEAVEFUNC(name) \
    ReleaseMutex(name##_mutex);
"""

@mark_section("minhook_decl")
def patch_minhook(inpath)->str:
    lines = read_lines(inpath)
    replace_map = {
        "MH_STATUS WINAPI": "MINHOOK_API MH_STATUS WINAPI",
        "const char *WINAPI": "MINHOOK_API const char* WINAPI"
    }
    lines = replace_lines(lines, replace_map, strip_left=True)
    return "".join(lines)

@mark_section("buffer_impl")
@ccode_replace(r"/\*(.|\n){,1000}MinHook(.|\n){,1000}DISCLAIMED(.|\n){,600}\*/", "", flags=re.MULTILINE)
def patch_buffer(inpath) -> str:
    lines_h = read_lines(os.path.splitext(inpath)[0] + ".h" , "utf_8_sig")
    lines_h = static_func(lines_h)
    lines_c = read_lines(os.path.splitext(inpath)[0] + ".c" , "utf_8_sig")
    lines_c = replace_lines(lines_c, {
        '#include "buffer.h"': "".join(lines_h)
    })
    return "".join(lines_c)

def patch_hde(hdepath, tablepath) -> str:
    lines_hde_h = read_lines(os.path.splitext(hdepath)[0] + ".h", "utf_8_sig")
    lines_hde_h = static_func(lines_hde_h)
    lines_hde_h = replace_lines(lines_hde_h, { 
        '#include "pstdint.h"': '//#include "pstdint.h"'
    })
    lines_table_h = read_lines(tablepath, "utf_8_sig")
    hdename = os.path.basename(os.path.splitext(hdepath)[0])
    tablename = os.path.basename(os.path.splitext(tablepath)[0])
    lines_hde_c = read_lines(os.path.splitext(hdepath)[0] + ".c", "utf_8_sig")
    lines_hde_c = replace_lines(lines_hde_c, {
        f'#include "{hdename}.h"': "".join(lines_hde_h),
        f'#include "{tablename}.h"': "".join(lines_table_h), 
    })

    return "".join(lines_hde_c)

@mark_section("trampoline_impl")  
@ccode_replace(r"/\*(.|\n){,1000}MinHook(.|\n){,1000}DISCLAIMED(.|\n){,600}\*/", "", flags=re.MULTILINE)
def patch_trampoline(trampolinepath, hdedir) -> str:
    lines_h = read_lines(os.path.splitext(trampolinepath)[0] + ".h", "utf_8_sig")
    lines_h = static_func(lines_h)
    lines_psdint_h = read_lines(os.path.join(hdedir, "pstdint.h"), "utf_8_sig")
    lines_hde32 = patch_hde(os.path.join(hdedir, "hde32.c"), os.path.join(hdedir, "table32.h"))
    lines_hde64 = patch_hde(os.path.join(hdedir, "hde64.c"), os.path.join(hdedir, "table64.h"))
    lines_c = read_lines(os.path.splitext(trampolinepath)[0] + ".c", "utf_8_sig")
    lines_c = replace_lines(lines_c, {
        '#include "trampoline.h"': "".join(lines_h), 
        '#include "buffer.h"' : '//#include "buffer.h"',
        '#include "./hde/hde32.h"': "".join(lines_hde32),
        '#include "./hde/hde64.h"': "".join(lines_hde64)
    })
    return "".join(lines_psdint_h) + "".join(lines_c)

@mark_section("hook_impl")
@ccode_replace(r"/\*(.|\n){,1000}MinHook(.|\n){,1000}DISCLAIMED(.|\n){,600}\*/", "", flags=re.MULTILINE)
def patch_hook(inpath) -> str:
    lines = read_lines(inpath, "utf_8_sig")
    lines = replace_lines(lines, {
        '#include "buffer.h"' : '//#include "buffer.h"',
        '#include "trampoline.h"': '//#include "trampoline.h"', 
        '#include "../include/MinHook.h"': '//#include "../include/MinHook.h"'
    })
    return "".join(lines)

def make_stb(repodir, info, version) -> str:
    stbdecl_ccode = make_stbdecl()
    mihookdecl_code = patch_minhook(os.path.join(repodir, "include/MinHook.h"))
    buffer_ccode = patch_buffer(os.path.join(repodir, "src/buffer.c"))
    trampoline_ccode = patch_trampoline(os.path.join(repodir, "src/trampoline.c"),
                                        os.path.join(repodir, "src/hde"))
    hook_ccode = patch_hook(os.path.join(repodir, "src/hook.c"))
    return f"""{info}
#ifndef _MINHOOK_H
#define _MINHOOK_H
#define MINHOOK_VERSION "{version}"
{stbdecl_ccode} 
{mihookdecl_code}

#ifdef MINHOOK_IMPLEMENTATION 
{buffer_ccode} 
{trampoline_ccode}
{hook_ccode}
#endif // MINHOOK_IMPLEMENTATION
#endif // _MINHOOK_H" 
"""

if __name__ == "__main__":
    srcdir = sys.argv[1] if len(sys.argv) > 1 else "depend/minhook" 
    outpath = sys.argv[2] if len(sys.argv) > 2 else "build/stb_minhook.h"
    version = sys.argv[3] if len(sys.argv) > 3 else "1.3.4"
    ccode = make_stb(srcdir, info, version)
    with open(outpath, "wt", encoding="utf-8", newline="\n") as fp:
        fp.write(ccode)
    outpath2 = f"{os.path.splitext(outpath)[0]}_v{version.replace('.', '_')}.h"
    with open(outpath2, "wt", encoding="utf-8", newline="\n") as fp:
        fp.write(ccode)