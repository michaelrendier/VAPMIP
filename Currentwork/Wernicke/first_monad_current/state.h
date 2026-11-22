/*
 * PtolC/state.h — Monad state load/save.
 *
 * A monad state file is the full field description of a monad at a specific
 * moment of its education: which zeros are occupied, how deep the β field sits,
 * which words are coupled through the A-matrix, and the current affect level.
 *
 * These are not checkpoints of a training process — they are states of an
 * education.  monad_wordnet.bin is the state of a monad educated by WordNet.
 * monad.bin is a pointer to whichever education is currently active.
 */

#ifndef STATE_H
#define STATE_H

#include "monad.h"

/* Load a monad state from path.
 * Returns 0 on success, -1 on error (prints reason to stderr). */
int state_load(Monad *m, const char *path);

/* Save current monad state to path.
 * Skips A entries below min_weight to cap file size.
 * Returns 0 on success, -1 on error. */
int state_save(const Monad *m, const char *path, double min_weight);

/* Load only the vocab section from path into m, replacing m->vocab and wm.
 * β, A, age, affect, and word_count are untouched.
 * Call state_load() first for the field state, then state_load_vocab() for
 * the Face layer:  state_load(m, "monad.bin"); state_load_vocab(m, "monad_wordnet.bin")
 * Returns 0 on success, -1 on error (N mismatch, bad magic, read failure). */
int state_load_vocab(Monad *m, const char *path);

#endif /* STATE_H */
