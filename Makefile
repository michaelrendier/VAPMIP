CC      = gcc
CFLAGS  = -O2 -Wall -Wextra -std=c99
LDFLAGS = -lm -lpthread
BINARY  = ptolemy-monad
PREFIX  = /usr/local

all: $(BINARY)

$(BINARY): monad.c auth_totp.c
	$(CC) $(CFLAGS) -o $(BINARY) monad.c auth_totp.c $(LDFLAGS)

totp-test: auth_totp.c
	$(CC) $(CFLAGS) -DTOTP_SELFTEST -o totp_test auth_totp.c

install: $(BINARY)
	pkexec install -m 755 $(abspath $(BINARY)) $(PREFIX)/bin/$(BINARY)

clean:
	rm -f $(BINARY) totp_test

.PHONY: all install clean totp-test
