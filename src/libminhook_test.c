#include <stdio.h>
#include <assert.h>

#if defined (_MSC_VER) 
#define NOINLINE __declspec(noinline)
#define MINHOOK_IMPLEMENTATION
#else
#define NOINLINE __attribute__((noinline))
#endif
#include "stb_minhook.h"

void *pold = NULL;
void *pnew = NULL;
void *ptarget = NULL;

typedef const char* (*PFN_print_hello)(int i);

// sometings, clang release might stiil inline this function, better to use debug type
NOINLINE const char *print_hello(int i)
{
    static char buf[0x256];
    sprintf(buf, "hello world %d", i);
    puts(buf);
    return buf;
}

NOINLINE const char *print_hello_hook(int i)
{
    static char buf[0x256];
    PFN_print_hello pfn_print_hello = (PFN_print_hello)pold;
    const char *res = pfn_print_hello(i);
    assert(res);
    sprintf(buf, "hello world hook %d", i);
    puts(buf);
    return buf;
}

int main(int argc, char *argv[])
{
    printf("%s ", argv[0]);
    #if defined(_MSC_VER)
    printf("compiler MSVC=%d\n", _MSC_VER);
    #elif defined(__GNUC__)
    printf("compiler GNUC=%d.%d\n", __GNUC__, __GNUC_MINOR__);
    #elif defined(__TINYC__)
    printf("compiler TCC\n");
    #endif

    // create hook
    ptarget = (void*)print_hello;
    pnew = (void*)print_hello_hook;
    MH_STATUS status = MH_Initialize();
    assert(status  == MH_OK);
    status = MH_CreateHook(ptarget, pnew, &pold);
    printf("MH_CreateHook %s\n", MH_StatusToString(status));
    
    // enable hook
    status = MH_EnableHook(ptarget);
    printf("MH_EnableHook %s\n", MH_StatusToString(status));
    const char *res1 = print_hello(1);
    assert(res1);
    assert(!strcmp(res1, "hello world hook 1")); // clang release build might inline to make not pass
    
    // disable hook
    status = MH_DisableHook(ptarget);
    printf("MH_DisableHook %s\n", MH_StatusToString(status));
    const char *res2 = print_hello(1);
    assert(res2);
    assert(!strcmp(res2, "hello world 1"));
    
    // uninstall hook
    status = MH_Uninitialize();
    assert(status == MH_OK);
    
    return 0;
}