# build example, tested in linux 10.0.0-3, gcc 12, wine-9.0
# make stbminhook
# make libminhook libminhook_test CC=i686-w64-mingw32-gcc BUILD_TYPE=32d
# make libminhook libminhook_test CC=x86_64-w64-mingw32-gcc BUILD_TYPE=64d

# general config
CC:=clang # clang (llvm-mingw), gcc (mingw-w64), tcc (x86 stdcall name has problem)
BUILD_TYPE:=32# 32, 32d, 64, 64d
BUILD_DIR:=dist
INCS:=-Isrc
LIBS:=-luser32
CFLAGS:=-fPIC -std=c99 \
	-fvisibility=hidden \
	-ffunction-sections -fdata-sections
LDFLAGS:=-Wl,--enable-stdcall-fixup \
		 -Wl,--kill-at \
		 -Wl,--gc-sections \
		 -D_WIN32_WINNT=0X0400 \
		 -Wl,--subsystem,console:4.0 # compatible for xp

# build config
ifneq (,$(findstring 64, $(BUILD_TYPE)))
CFLAGS+=-m64
else
CFLAGS+=-m32
endif
ifneq (,$(findstring d, $(BUILD_TYPE)))
CFLAGS+=-g -D_DEBUG
else
CFLAGS+=-Os
endif
ifneq (,$(findstring tcc, $(CC)))
LDFLAGS= # tcc can not remove at at stdcall in i686
else
endif

all: prepare stb_minhook libminhook libminhook_test

clean:
	@rm -rf $(BUILD_DIR)/*minhook*

prepare:
	@if ! [ -d $(BUILD_DIR) ]; then mkdir -p $(BUILD_DIR); fi

stbminhook: script/build_stb_minhook.py
	@echo "## $@"
	python $< depend/minhook dist/stb_minhook.h
	cp -f dist/stb_minhook.h src/stb_minhook.h

libminhook: src/libminhook.c
	@echo "## $@"
	$(CC) $< -o $(BUILD_DIR)/$@$(BUILD_TYPE).dll \
		-shared $(INCS) $(LIBS) \
		$(CFLAGS) $(LDFLAGS) 

libminhook_test: test/minhook_test.c
	$(CC) $< -o $(BUILD_DIR)/$@$(BUILD_TYPE).dll \
		$(INCS) $(LIBS) \
		$(CFLAGS) $(LDFLAGS) 

.PHONY: all clean prepare stb_minhook libminhook libminhook_test