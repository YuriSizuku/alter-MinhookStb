msbuild libminhook.sln -t:libminhook_test:rebuild -p:configuration=debug -p:Platform=x86 
msbuild libminhook.sln -t:libminhook_test:rebuild -p:configuration=debug -p:Platform=x64
pushd build
libminhook_test32d
libminhook_test64d
popd