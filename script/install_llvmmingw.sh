echo "install mingwsdk to ${MINGWSDK}"
if ! [ -d ${MINGWSDK} ]; then
    if [ -n "$(uname -a | grep Linux)" ]; then
        curl -fsSL https://github.com/mstorsjo/llvm-mingw/releases/download/20240619/llvm-mingw-20240619-msvcrt-ubuntu-20.04-x86_64.tar.xz -o /tmp/llvm-mingw.tar.xz
        tar xf /tmp/llvm-mingw.tar.xz -C /tmp
        _tmppath=/tmp/llvm-mingw-20240619-msvcrt-ubuntu-20.04-x86_64 
        mv -f ${_tmppath} $MINGWSDK || echo "try to use sudo mv to $MINGWSDK" && sudo mv -f ${_tmppath} $MINGWSDK
        rm -rf /tmp/llvm-mingw.tar.xz
    else
        curl -fsSL https://github.com/mstorsjo/llvm-mingw/releases/download/20240619/llvm-mingw-20240619-msvcrt-x86_64.zip -o ~/llvm-mingw.zip
        7z x ~/llvm-mingw.zip -o$HOME
        mv -f ~/llvm-mingw-20240619-msvcrt-x86_64 $MINGWSDK
        rm -rf ~/llvm-mingw.zip
    fi
fi