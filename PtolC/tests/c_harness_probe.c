/* c_harness_probe.c -- a command-line probe of monad_harness.c's ears, driven by tests/test_c_parity.py (the Python monad is the reference).
 * cc -O2 -I.. -o c_harness_probe c_harness_probe.c ../monad_harness.c ../monad.c ../tokenizer.c ../filter.c -lm
 * stdin, one command per line:  N <text> | M <text> | D <w> <b> <active> | T <fill>|<text> (user turn, state kept) | H <cls>|<pair>|<text> | R <word> | K <word>... (known set) */
#include "../monad_harness.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static char known_set[200000]; 
static int known(const char *w, void *c) { (void)c; char k[130]; snprintf(k, sizeof k, " %s ", w); return strstr(known_set, k) != NULL; }
static double pgen(const char *w, void *c) { (void)c; (void)w; return 1e-4; }

int main(int argc, char **argv)
{
    const char *dir = argc > 1 ? argv[1] : "/tmp/mh_probe"; const char *pd = argc > 2 ? argv[2] : "..";
    char mk[600]; snprintf(mk, sizeof mk, "mkdir -p %s", dir); if (system(mk)) return 2;
    strcpy(known_set, " ");
    mh_ear *e = mh_ear_open(dir, pd, known, pgen, NULL); char line[70000];
    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line); if (L && line[L - 1] == '\n') line[--L] = 0;
        if (line[0] == 'N') {
            static char out[70000]; mh_number nm[64]; int n = mh_split_numbers(line + 2, out, sizeof out, nm, 64);
            printf("N\t%s\t%d", out, n); for (int i = 0; i < n; i++) printf("\t%s|%s|%.10g|%d", nm[i].text, nm[i].kind, nm[i].value, nm[i].has_value); printf("\n");
        } else if (line[0] == 'M') {
            double d[14]; if (!mh_meter_raw(e, line + 2, d)) { printf("M\tNOMODEL\n"); continue; }
            printf("M"); for (int p = 0; p < 14; p++) printf("\t%.6f", d[p]); printf("\n");
        } else if (line[0] == 'D') {
            double w, b; int act; sscanf(line + 2, "%lf %lf %d", &w, &b, &act); double dl, g; double c = mh_bw_correction(w, b, &act, &dl, &g);
            printf("D\t%.9f\t%.9f\t%d\t%.9f\n", dl, g, act, c);
        } else if (line[0] == 'T') {
            int fill = atoi(line + 2); char *bar = strchr(line + 2, '|'); mh_state st; mh_ear_user_turn(e, bar + 1, fill, &st);
            int ax, lv; mh_state_heard(&st, &ax, &lv); int tx[5], tl[5]; mh_state_trajectory(&st, 5, tx, tl);
            printf("T\t%d\t%d\t%d\t%d\t%.4f", st.ready, st.held, st.healed, lv, st.k_eff); printf("\t%s", MH_AXES[ax]);
            for (int a = 0; a < MH_NAX; a++) printf("\t%.4f", st.mix[a]); for (int a = 0; a < MH_NAX; a++) printf("\t%.2f", st.target[a]);
            for (int i = 0; i < 5; i++) printf("\t%s:%d", MH_AXES[tx[i]], tl[i]); for (int p = 0; p < 14; p++) printf("\t%.4f", st.conc[p]); printf("\n");
        } else if (line[0] == 'H') {
            int cls = atoi(line + 2); char *b1 = strchr(line + 2, '|'); char *b2 = strchr(b1 + 1, '|'); *b2 = 0; int nn = mh_ear_hear(e, b2 + 1, cls, b1 + 1);
            printf("H\t%d\t%ld\t%.9f\t%.9f\n", nn, (long)mh_ear_n_obs(e), mh_ear_lambda(e), mh_ear_bw_correction(e));
        } else if (line[0] == 'R') {
            printf("R\t%.9g\t%.9f\n", mh_ear_p_word(e, line + 2), mh_ear_bits_per_word(e, line + 2));
        } else if (line[0] == 'K') { strncat(known_set, line + 2, sizeof known_set - strlen(known_set) - 3); strcat(known_set, " "); }
    }
    mh_ear_close(e); return 0;
}
