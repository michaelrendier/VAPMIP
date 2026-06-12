/*
 * ptol.c — Sedenion geometry engine.
 *
 * usage: ptol [-r] <prompt>
 *
 * Projects input string onto 16 sedenion basis elements e0..e15 via
 * Dirichlet-weighted inner product at σ=½:
 *
 *   x_k = Σ_{i=1}^{N}  c_i · i^(-½) · cos(2π·i / p_k)
 *
 * σ=½ weight is Noether forcing — not a free parameter.
 * Prime frequencies are the zero-free-parameter basis: {2,3,5,...,53}.
 *
 * The response is the shadow of the geometry.
 * These scalars are the geometry.  The words are the shadow.
 *
 * Flags:
 *   -r   raw mode: 16 scalars + primes, machine-readable (for piping to output layers)
 *
 * Output (default):
 *   sedenion:   16 unit scalars, one per line
 *   primes:     active primes (|x_k| >= peak/φ)
 *   spiral:     dimension order from zero divisor outward (ascending |x_k|)
 *
 * Output (-r):
 *   16 floats, one per line
 *   ---
 *   active primes, one per line
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "ptolemy.h"

static const int P[16] = {
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53
};

static double project(const unsigned char *s, int n, int k)
{
    double sum  = 0.0;
    double freq = 2.0 * M_PI / (double)P[k];
    for (int i = 1; i <= n; i++)
        sum += (double)s[i-1] * pow((double)i, -0.5) * cos(freq * (double)i);
    return sum;
}

static int cmp_mag_asc(const void *a, const void *b)
{
    const int *ia = (const int *)a, *ib = (const int *)b;
    extern double _x[16];
    double da = fabs(_x[*ia]), db = fabs(_x[*ib]);
    return (da > db) - (da < db);
}

double _x[16];

int main(int argc, char *argv[])
{
    int raw  = 0;
    int arg0 = 1;

    if (argc >= 2 && strcmp(argv[1], "-r") == 0) {
        raw  = 1;
        arg0 = 2;
    }

    if (argc <= arg0) {
        fprintf(stderr, "usage: ptol [-r] <prompt>\n");
        return 1;
    }

    char sigma[65536];
    sigma[0] = '\0';
    for (int i = arg0; i < argc; i++) {
        if (i > arg0) strncat(sigma, " ", sizeof(sigma) - strlen(sigma) - 1);
        strncat(sigma, argv[i], sizeof(sigma) - strlen(sigma) - 1);
    }
    int n = (int)strlen(sigma);

    double norm = 0.0, peak = 0.0;
    for (int k = 0; k < 16; k++) {
        _x[k] = project((const unsigned char *)sigma, n, k);
        norm  += _x[k] * _x[k];
        if (fabs(_x[k]) > peak) peak = fabs(_x[k]);
    }
    norm = sqrt(norm);

    double v[16];
    for (int k = 0; k < 16; k++)
        v[k] = (norm > 0.0) ? _x[k] / norm : 0.0;

    double thresh = peak / MONAD_PHI;

    if (raw) {
        for (int k = 0; k < 16; k++)
            printf("%+.10f\n", v[k]);
        printf("---\n");
        for (int k = 0; k < 16; k++)
            if (fabs(_x[k]) >= thresh)
                printf("%d\n", P[k]);
        return 0;
    }

    /* Human-readable output. */
    printf("sedenion:\n");
    for (int k = 0; k < 16; k++)
        printf("  e%-2d  %+.8f\n", k, v[k]);

    printf("\nprimes:\n");
    for (int k = 0; k < 16; k++)
        if (fabs(_x[k]) >= thresh)
            printf("  p%-2d = %d\n", k, P[k]);

    /* Spiral order: dimensions from zero divisor outward (ascending |x|). */
    int idx[16];
    for (int k = 0; k < 16; k++) idx[k] = k;
    qsort(idx, 16, sizeof(int), cmp_mag_asc);

    printf("\nspiral (zero divisor → great circle):\n  ");
    for (int i = 0; i < 16; i++)
        printf("e%d(%+.3f)%s", idx[i], v[idx[i]], i < 15 ? " → " : "\n");

    return 0;
}
