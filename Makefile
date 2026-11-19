QDOS_CC ?= qdos-gcc
CFLAGS = -O2 -Wall

all: bin/ls bin/ls_rext

build/ls: ls_c
	mkdir -p build
	$(QDOS_CC) $(CFLAGS) -x c ls_c -o $@

bin/ls: build/ls package.py
	mkdir -p bin
	python3 package.py build/ls $@

test: bin/ls bin/ls_rext
	python3 tests/test_ls.py
	python3 tests/test_package.py

.PHONY: all test

QDOS_BINDIR = $(dir $(shell command -v $(QDOS_CC)))
QDOS_LIBDIR = $(abspath $(QDOS_BINDIR)/../lib)

build/rext/crt.o: ls_rext.s
	mkdir -p build/rext
	$(QDOS_BINDIR)qdos-as $< -o $@

build/rext/empty.o:
	mkdir -p build/rext
	printf '        .sect .text\n' > build/rext/empty.s
	$(QDOS_BINDIR)qdos-as build/rext/empty.s -o $@

build/rext/linked: build/rext/crt.o build/rext/empty.o
	cd build/rext && $(QDOS_BINDIR)qdos-ld -L. -L$(QDOS_LIBDIR) -o $(CURDIR)/$@ empty.o

bin/ls_rext: build/rext/linked Makefile
	mkdir -p bin
	python3 -c 'from pathlib import Path; data = Path("$<").read_bytes(); assert data[-8:-4] == b"XTcc", "Missing linker trailer"; Path("$@").write_bytes(data[:-8])'

test-launcher: bin/ls_rext
	python3 tests/test_ls_rext.py

.PHONY: test-launcher
