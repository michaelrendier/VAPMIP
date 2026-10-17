# tools/c_nlp/Makefile — C programs that reach WordNet and NLTK.
#   make        builds both
#   make run    runs both (needs the system python3 with nltk and ~/nltk_data, and /usr/share/wordnet)
# NLTK has no C API; nltk_embed_test embeds CPython (python3-dev).  wn_c_test uses the native WordNet 3.0 C library (wordnet-dev).
CC ?= cc
all: wn_c_test nltk_embed_test
wn_c_test: wn_c_test.c
	$(CC) -Wall -o $@ $< -lwordnet
nltk_embed_test: nltk_embed_test.c
	$(CC) -Wall -o $@ $< $(shell python3-config --embed --cflags --ldflags)
run: all
	./wn_c_test
	./nltk_embed_test
clean:
	rm -f wn_c_test nltk_embed_test
.PHONY: all run clean
