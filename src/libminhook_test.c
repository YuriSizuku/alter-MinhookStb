#include <stdio.h>
#include <assert.h>

#if defined (_MSC_VER) 
#define MINHOOK_IMPLEMENTATION
#endif
#include "stb_minhook.h"

void *pold = NULL;
void *pnew = NULL;
void *ptarget = NULL;

typedef const char* (*PFN_print_hello)(int i);

const char *print_hello(int i)
{
    static char buf[0x256];
    sprintf(buf, "hello world %d", i);
    puts(buf);
    return buf;
}

const char *print_hello_hook(int i)
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

    ptarget = (void*)print_hello;
    pnew = (void*)print_hello_hook;
    assert(MH_Initialize() == MH_OK);
    MH_STATUS  status = MH_CreateHook(ptarget, pnew, &pold);
    printf("MH_CreateHook %s\n", MH_StatusToString(status));
    
    // enable hook
    status = MH_EnableHook(ptarget);
    printf("MH_EnableHook %s\n", MH_StatusToString(status));
    const char *res1 = print_hello(1);
    assert(res1);
    assert(!strcmp(res1, "hello world hook 1"));
    
    // disable hook
    status = MH_DisableHook(ptarget);
    printf("MH_DisableHook %s\n", MH_StatusToString(status));
    const char *res2 = print_hello(1);
    assert(res2);
    assert(!strcmp(res2, "hello world 1"));
    
    // uninstall hook
    assert(MH_Uninitialize() == MH_OK);
    
    return 0;
}