CC      = gcc
CFLAGS  = -O2 -Wall -Wextra -std=c99
LDFLAGS = -lm -lpthread
BINARY  = ptolemy-monad
PREFIX  = /usr/local

all: $(BINARY)

$(BINARY): monad.c
	$(CC) $(CFLAGS) -o $(BINARY) monad.c $(LDFLAGS)

install: $(BINARY)
	pkexec install -m 755 $(abspath $(BINARY)) $(PREFIX)/bin/$(BINARY)

clean:
	rm -f $(BINARY)

.PHONY: all install clean
