/* nltk_embed_test.c — C calling NLTK by embedding CPython.  NLTK has no C API; this is the supported route
 * (python3-dev is installed).  It asks NLTK for: WordNet synsets of "play", the VerbNet 3.x classes of "play",
 * and a part-of-speech tag of a sentence, then prints them.  Build:
 *   cc -o nltk_embed_test nltk_embed_test.c $(python3-config --embed --cflags --ldflags)
 * Run with the Python whose site-packages hold nltk (the system python3, or set PYTHONHOME/PYTHONPATH). */
#include <Python.h>
#include <stdio.h>

static const char *CODE =
"import nltk\n"
"from nltk.corpus import wordnet as wn, verbnet as vn\n"
"print('nltk', nltk.__version__)\n"
"print('wordnet synsets of play:', len(wn.synsets('play')), '| first:', wn.synsets('play')[0].name(), '-', wn.synsets('play')[0].definition()[:50])\n"
"print('verbnet classes of play:', vn.classids('play')[:5])\n"
"print('tagged:', nltk.pos_tag(nltk.word_tokenize('can you play the piano')))\n";

int main(void) {
    Py_Initialize();
    int rc = PyRun_SimpleString(CODE);
    if (Py_FinalizeEx() < 0) return 2;
    return rc ? 1 : 0;
}
