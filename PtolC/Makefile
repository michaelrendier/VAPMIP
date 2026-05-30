# PtolC/Makefile — C Monad build

CC      = gcc
CFLAGS  = -O2 -Wall -Wextra -std=c11 -D_POSIX_C_SOURCE=200809L
LDFLAGS = -lm

# ── Optional: libxml2 (HTML/XML extraction) ───────────────────────────────────
HAVE_XML := $(shell pkg-config --exists libxml-2.0 2>/dev/null && echo yes)
ifeq ($(HAVE_XML),yes)
    CFLAGS  += -DHAVE_LIBXML2 $(shell pkg-config --cflags libxml-2.0)
    LDFLAGS += $(shell pkg-config --libs libxml-2.0)
endif

TARGET  = ptolemy
SRCS    = main.c monad.c state.c tokenizer.c filter.c ingest.c log.c daemon.c \
          search.c sensor.c code.c
OBJS    = $(SRCS:.c=.o)

PREFIX       ?= /usr/local
MANDIR       ?= $(PREFIX)/share/man
PTOLEMY_HOME ?= $(HOME)/.ptolemy

.PHONY: all clean export corpus grammar full expand ingest install install-man install-systemd link

all: $(TARGET)

# ── Corpus: download WordNet + ingest → monad_wordnet.bin ───────────────────
# Requires Python 3 + NLTK.  Run by user — not automated.
# Usage: make corpus
corpus: $(TARGET)
	@echo "[corpus] checking NLTK wordnet…"
	@python3 -m nltk.downloader -q wordnet 2>/dev/null || \
	    (pip install --quiet nltk && python3 -m nltk.downloader -q wordnet)
	@echo "[corpus] extracting lemmas + definitions (313K lines)…"
	@python3 tools/dump_wordnet.py | ./$(TARGET) -i -L -
	@echo "[corpus] done → monad_wordnet.bin"

# ── Grammar: ingest function-word lexicon + install for auto-reanchor ───────
# Usage: make grammar
grammar: $(TARGET)
	@echo "[grammar] ingesting English function-word lexicon…"
	@./$(TARGET) -l corpora/english_grammar.txt
	@mkdir -p $(PTOLEMY_HOME)
	@cp corpora/english_grammar.txt $(PTOLEMY_HOME)/english_grammar.txt
	@echo "[grammar] installed → $(PTOLEMY_HOME)/english_grammar.txt"
	@echo "[grammar] done — auto-reanchor after -I is now active"

# ── Link: set monad.bin → active education state ────────────────────────────
# monad.bin is the pointer to the currently active language/education state.
# Usage: make link STATE=monad_wordnet.bin
STATE ?= monad_wordnet.bin
link:
	@mkdir -p $(PTOLEMY_HOME)
	@ln -sf $(PTOLEMY_HOME)/$(STATE) $(PTOLEMY_HOME)/monad.bin
	@echo "[state] monad.bin → $(STATE)"

# ── Full: binary + corpus in one step ───────────────────────────────────────
full: $(TARGET) corpus

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

# Export Python state to binary (run from Ptolemy3/ root)
export:
	python3 ../Callimachus/checkpoint_export.py

# Expand state zero field — usage: make expand N=255400
expand: tools/checkpoint_expand
	./tools/checkpoint_expand $(PTOLEMY_HOME)/monad.bin $(N)

tools/checkpoint_expand: tools/checkpoint_expand.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Full system ingest — usage: make ingest  (or: make ingest FIRST=/SystemTree.txt)
FIRST ?= /SystemTree.txt
ingest: $(TARGET)
	python3 tools/ingest_system.py --root / --first $(FIRST)

# ── Install ──────────────────────────────────────────────────────────────────
install: $(TARGET) install-man
	install -Dm755 $(TARGET) $(DESTDIR)$(PREFIX)/bin/ptolemy
	install -Dm755 tools/checkpoint_expand $(DESTDIR)$(PREFIX)/bin/checkpoint_expand

install-systemd:
	install -Dm644 systemd/ptolemy.socket \
	    $(DESTDIR)$(PREFIX)/lib/systemd/user/ptolemy.socket
	install -Dm644 systemd/ptolemy.service \
	    $(DESTDIR)$(PREFIX)/lib/systemd/user/ptolemy.service
	@echo "Enable with: systemctl --user enable --now ptolemy.socket"

install-man:
	install -Dm644 man/ptolemy.1 $(DESTDIR)$(MANDIR)/man1/ptolemy.1
	install -Dm644 man/ptolemyignore.5 $(DESTDIR)$(MANDIR)/man5/ptolemyignore.5
	gzip -f $(DESTDIR)$(MANDIR)/man1/ptolemy.1
	gzip -f $(DESTDIR)$(MANDIR)/man5/ptolemyignore.5

# ── Remove build artifacts ────────────────────────────────────────────────────
clean:
	rm -f $(OBJS) $(TARGET) tools/checkpoint_expand
	rm -f ~/.ptolemy/logs/ptolemy_test_*.log 2>/dev/null || true

# ── Dependencies ────────────────────────────────────────────────────────────
main.o:       main.c ptolemy.h monad.h state.h tokenizer.h ingest.h daemon.h log.h
monad.o:      monad.c ptolemy.h monad.h filter.h tokenizer.h
state.o:      state.c ptolemy.h state.h monad.h
tokenizer.o:  tokenizer.c tokenizer.h
filter.o:     filter.c filter.h
ingest.o:     ingest.c monad.h filter.h state.h ingest.h log.h
log.o:        log.c log.h
daemon.o:     daemon.c ptolemy.h monad.h state.h daemon.h log.h search.h sensor.h code.h
search.o:     search.c search.h log.h
sensor.o:     sensor.c sensor.h log.h
code.o:       code.c code.h log.h
