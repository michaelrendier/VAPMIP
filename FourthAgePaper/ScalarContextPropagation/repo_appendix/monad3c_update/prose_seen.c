/* Standalone extraction of the prose_seen ladder from
 * PtolC/monad.c::monad_learn_ex (lines ~505-512). ft is the file-type
 * tag the caller passes: NS_FT_WORDNET (the canonical dictionary source)
 * vs NS_FT_PROSE (real running text). */
#include <stdio.h>

typedef enum { FT_PROSE, FT_WORDNET } FType;

int step(int prose_seen, FType ft) {
    if (ft == FT_WORDNET) {
        prose_seen = 2;                         /* canonical dictionary */
    } else {                                    /* FT_PROSE */
        if (prose_seen == 0)      prose_seen = 1;  /* prose only */
        else if (prose_seen == 2) prose_seen = 3;  /* WN + prose = verified */
    }
    return prose_seen;
}

int main(void) {
    const char *NAME[] = {"unseen", "prose-only", "WordNet-only", "verified common"};

    int a = 0;
    printf("word A: WordNet first, then prose\n");
    a = step(a, FT_WORDNET); printf("  after WordNet sighting: %d (%s)\n", a, NAME[a]);
    a = step(a, FT_PROSE);   printf("  after prose sighting:   %d (%s)\n", a, NAME[a]);

    int b = 0;
    printf("\nword B: prose first, then WordNet\n");
    b = step(b, FT_PROSE);   printf("  after prose sighting:   %d (%s)\n", b, NAME[b]);
    b = step(b, FT_WORDNET); printf("  after WordNet sighting: %d (%s)\n", b, NAME[b]);

    int c = 0;
    printf("\nword C: prose only, three times\n");
    for (int i = 0; i < 3; i++) {
        c = step(c, FT_PROSE);
        printf("  sighting %d: %d (%s)\n", i + 1, c, NAME[c]);
    }
    return 0;
}
