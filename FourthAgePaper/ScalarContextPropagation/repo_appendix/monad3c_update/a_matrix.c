/* Standalone extraction of the A-matrix coupling law from
 * PtolC/monad.c::monad_learn_ex (lines ~538-572), real MONAD_GAP from
 * ptolemy.h. Simplified: the real function also multiplies by a x2
 * "same Dirac pole" bonus (dirac_pole(zeros[i])==dirac_pole(zeros[j]));
 * that bonus is NOT reproduced here -- this shows the base 2D
 * inverse-distance law only, honestly labeled as a partial extraction. */
#include <stdio.h>
#include <math.h>

#define MONAD_GAP 0.000707

double edge_weight(double E_i, double E_j, double gamma_i, double gamma_j, int d_text) {
    double d_zero = fabs(gamma_i - gamma_j) + MONAD_GAP;
    return E_i * E_j / (d_zero * (double)d_text);
}

int main(void) {
    /* three words in a sentence, illustrative E and gamma values */
    double E[3]     = {0.42, 0.38, 0.51};
    double gamma[3] = {14.134725, 21.022040, 25.010858};
    const char *w[3] = {"crankshaft", "precession", "rotor"};

    printf("pair                    text_dist  zero_dist      weight\n");
    for (int i = 0; i < 3; i++) {
        for (int j = i + 1; j < 3; j++) {
            int d_text = j - i;
            double d_zero = fabs(gamma[i] - gamma[j]) + MONAD_GAP;
            double wgt = edge_weight(E[i], E[j], gamma[i], gamma[j], d_text);
            printf("%-11s <-> %-11s  %6d     %10.6f   %.8f\n",
                   w[i], w[j], d_text, d_zero, wgt);
        }
    }
    return 0;
}
