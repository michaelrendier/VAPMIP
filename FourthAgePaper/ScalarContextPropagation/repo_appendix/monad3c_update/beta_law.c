/* Standalone extraction of the core beta-update arithmetic from
 * PtolC/monad.c::monad_learn_ex (lines ~490-494), using the real
 * constants from PtolC/ptolemy.h. NOT linked against the full Monad
 * struct -- isolates just the formula for demonstration. */
#include <stdio.h>
#include <math.h>

#define MONAD_ALPHA_LEARN 0.01
#define MONAD_BETA_SAT    7.552

double learn_step(double beta, double E, double zero_gamma) {
    double amp = fabs(sin(zero_gamma)) * (M_PI * 0.5);
    double nb  = beta + E * E * MONAD_ALPHA_LEARN * amp;
    if (nb > MONAD_BETA_SAT) nb = MONAD_BETA_SAT;
    return nb;
}

int main(void) {
    /* A word seen 5 times in a row -- same E, same zero (address fixed) */
    double beta = 0.0;
    double E = 0.42;        /* illustrative spectral energy for one word */
    double gamma = 14.134725; /* first nontrivial Riemann zero, illustrative */

    printf("sight  beta_before   beta_after   delta\n");
    for (int i = 1; i <= 5; i++) {
        double before = beta;
        beta = learn_step(beta, E, gamma);
        printf("%3d    %.6f     %.6f     +%.6f\n", i, before, beta, beta - before);
    }
    return 0;
}
