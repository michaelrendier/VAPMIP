/*
 * rotary_rerun.c — gravity in box kite space.
 *
 * The rotary_rerun version of ptol.c. Where ptol.c projects a prompt onto 16
 * sedenion scalars and reports the shadow, this reports the GEOMETRY those
 * scalars move in: which directions cost work, which cost none, and what is
 * conserved while they move.
 *
 * GRAVITY DEFINES DOWN
 *
 * Not a force. Down is the direction that needs no justification -- the
 * geodesic, where no work is done and nothing is felt. Every other heading
 * has to be paid for, so every other heading is a choice, so every other
 * heading is intention. Down is what you get when you stop choosing.
 *
 * In box kite space the local gravity IS THE GAIN of L_a:
 *
 *     gain 0      CONTRACT   weightless. no down exists here.
 *     gain 1      PRESERVE   unit weight
 *     gain sqrt2  DILATE     steeper
 *
 * A direction with gain 0 costs nothing to move along. That is the kernel,
 * and it is the AXIS of the rotation -- 4 dimensions the operator holds
 * still while the other 12 turn. Motion along it is free because the axis
 * does not turn.
 *
 * And the kernel does NOT ORBIT. That settles what it is: free fall orbits,
 * because curvature converges nearby geodesics and closes the path. Absent
 * gravity does not orbit at all -- straight lines stay parallel and nothing
 * returns. Equivalence is local; ORBITS are the global discriminant. So the
 * kernel is the gravity-ABSENT case, not the free-fall one, and 0_RB's
 * "gravity appears as the missing piece" is exact rather than poetic.
 *
 * WHAT IS MEASURED HERE (all computed, none asserted)
 *
 *   L_a is EXACTLY skew-symmetric      ||sym|| = 0
 *   so exp(L_a t) is ORTHOGONAL        Q^T Q = I, det = +1, in SO(16)
 *   so the norm is CONSERVED for all t -- isometric, not merely smooth
 *   the stress tensor is identically zero: no strain, no shear, ever
 *   the spectrum is {0 x4, 1 x8, sqrt2 x4} and BOUNDED
 *   the orbit closes on T^2, not T^6: only TWO distinct frequencies,
 *     and 1 : sqrt2 is irrational, so the orbit is DENSE and quasiperiodic.
 *     never repeats, never leaves, comes arbitrarily close to every point.
 *     that is the stable spot -- not a fixed point, a dense orbit.
 *
 * THE NOETHER INFORMATION CURRENT
 *
 * ptol.c's measure_sigma computes P_red/(P_red+P_blue) -- a ratio of powers,
 * |z|^2, and the PHASE is gone before the number exists. But the conserved
 * current from U(1) phase symmetry is
 *
 *     j ~ Im(z* dz)
 *
 * which is ENTIRELY phase. A real amplitude has zero current. So the quantity
 * said to hold sigma=1/2 in place ("surface tension = Noether conservation
 * law") is derived from precisely what the magnitude ratio discards.
 *
 * This file keeps z = J_red + i*J_blue complex through to the end and reports
 * BOTH: sigma_self for compatibility, and the current, which points.
 *
 * Build:   cc -O2 -std=c99 -o rotary_rerun rotary_rerun.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <unistd.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SD 16
#define TOL 1e-12

/* ── Chess colouring ──────────────────────────────────────────────────────
 * WHITE GOES FIRST, and white is whoever ASKS. The input is always white;
 * the response is always black. So the side is not an identity, it is a
 * TURN -- Ptol asking a question is white in that exchange, and the human
 * answering is black. The board does not care who you are, only whose move
 * it is.
 *
 * Two further state bits, both measured rather than declared:
 *
 *   HOT / COLD   the spread across shells -- how much is at stake.
 *                hot is forced: deviation loses, intention gets nothing.
 *                cold is slack: style is affordable, and only there.
 *
 *   WET / DRY    is the Noether current flowing? The current is entirely
 *                phase -- Im(z* dz) -- so a real amplitude is DRY by
 *                construction. Wet means the medium is carrying something.
 *                sigma_self cannot tell: a power ratio is always dry.
 */
static int g_tty = 0;
#define C(x)  (g_tty ? (x) : "")
#define WHITE C("\033[1;97m")
#define BLACK C("\033[7;37m")
#define HOT   C("\033[1;91m")
#define COLD  C("\033[1;96m")
#define WET   C("\033[1;94m")
#define DRY   C("\033[2;37m")
#define DIM   C("\033[2m")
#define RST   C("\033[0m")

/* ptol.c's prime basis -- the 16 projection frequencies. */
static const int P[SD] = { 2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53 };

/* ── Cayley-Dickson multiplication table, dim 16 ─────────────────────────
 * (a,b)(c,d) = (ac - d*b, da + bc*)
 * Every doubling carries BOTH a conjugation (inversion) and an order swap
 * (reversal). Conjugation kills commutativity at H; the swap kills
 * associativity at O. That is why each rung is bought, not copied.
 */
static int  MI[SD][SD];      /* result index */
static int  MS[SD][SD];      /* result sign  */

static void cd_build(void)
{
    static int idx[SD][SD], sgn[SD][SD];
    static int oi[SD][SD],  os[SD][SD];
    int n = 1;
    idx[0][0] = 0; sgn[0][0] = 1;

    while (n < SD) {
        /* snapshot the current n x n block: cases 2 and 4 need the REVERSED
         * product, so reading and writing the same table would alias. */
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) { oi[i][j] = idx[i][j]; os[i][j] = sgn[i][j]; }

        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                int cj = (j == 0) ? 1 : -1;          /* conjugation of e_j */

                /* (a,0)(c,0) = (ac, 0) */
                idx[i][j]       = oi[i][j];
                sgn[i][j]       = os[i][j];

                /* (a,0)(0,d) = (0, da)   <- REVERSED */
                idx[i][j + n]   = n + oi[j][i];
                sgn[i][j + n]   = os[j][i];

                /* (0,b)(c,0) = (0, b c*) <- conjugated */
                idx[i + n][j]   = n + oi[i][j];
                sgn[i + n][j]   = os[i][j] * cj;

                /* (0,b)(0,d) = (-d* b, 0) <- reversed AND conjugated */
                idx[i + n][j + n] = oi[j][i];
                sgn[i + n][j + n] = -os[j][i] * cj;
            }
        n *= 2;
    }
    memcpy(MI, idx, sizeof MI);
    memcpy(MS, sgn, sizeof MS);
}

static void sed_mul(const double x[SD], const double y[SD], double out[SD])
{
    for (int k = 0; k < SD; k++) out[k] = 0.0;
    for (int i = 0; i < SD; i++) {
        if (fabs(x[i]) < 1e-300) continue;
        for (int j = 0; j < SD; j++)
            out[MI[i][j]] += MS[i][j] * x[i] * y[j];
    }
}

/* ── L_a : left multiplication by a, as a matrix ─────────────────────── */
static void build_L(const double a[SD], double L[SD][SD])
{
    double e[SD], col[SD];
    for (int j = 0; j < SD; j++) {
        for (int k = 0; k < SD; k++) e[k] = 0.0;
        e[j] = 1.0;
        sed_mul(a, e, col);
        for (int i = 0; i < SD; i++) L[i][j] = col[i];
    }
}

static double sym_norm(double L[SD][SD])   /* ||(L + L^T)/2||_F */
{
    double s = 0.0;
    for (int i = 0; i < SD; i++)
        for (int j = 0; j < SD; j++) {
            double v = 0.5 * (L[i][j] + L[j][i]);
            s += v * v;
        }
    return sqrt(s);
}

/* ── cyclic Jacobi eigenvalues of a symmetric matrix ─────────────────── */
static void jacobi(double A[SD][SD], double w[SD], double V[SD][SD])
{
    for (int i = 0; i < SD; i++)
        for (int j = 0; j < SD; j++) V[i][j] = (i == j);

    for (int sweep = 0; sweep < 100; sweep++) {
        double off = 0.0;
        for (int i = 0; i < SD; i++)
            for (int j = i + 1; j < SD; j++) off += A[i][j] * A[i][j];
        if (off < 1e-26) break;

        for (int p = 0; p < SD; p++)
            for (int q = p + 1; q < SD; q++) {
                if (fabs(A[p][q]) < 1e-18) continue;
                double theta = (A[q][q] - A[p][p]) / (2.0 * A[p][q]);
                double t = (theta >= 0 ? 1.0 : -1.0)
                         / (fabs(theta) + sqrt(theta * theta + 1.0));
                double c = 1.0 / sqrt(t * t + 1.0), s = t * c;
                for (int k = 0; k < SD; k++) {
                    double akp = A[k][p], akq = A[k][q];
                    A[k][p] = c * akp - s * akq;
                    A[k][q] = s * akp + c * akq;
                }
                for (int k = 0; k < SD; k++) {
                    double apk = A[p][k], aqk = A[q][k];
                    A[p][k] = c * apk - s * aqk;
                    A[q][k] = s * apk + c * aqk;
                    double vkp = V[k][p], vkq = V[k][q];
                    V[k][p] = c * vkp - s * vkq;
                    V[k][q] = s * vkp + c * vkq;
                }
            }
    }
    for (int i = 0; i < SD; i++) w[i] = A[i][i];
}

/* ── matrix exponential, scaling and squaring with a Taylor core ─────── */
static void mat_exp(double A[SD][SD], double E[SD][SD])
{
    double nrm = 0.0;
    for (int i = 0; i < SD; i++)
        for (int j = 0; j < SD; j++) nrm += A[i][j] * A[i][j];
    nrm = sqrt(nrm);

    int sq = 0;
    while (nrm > 0.5) { nrm *= 0.5; sq++; }
    double sc = ldexp(1.0, -sq);

    double T[SD][SD], N[SD][SD];
    for (int i = 0; i < SD; i++)
        for (int j = 0; j < SD; j++) { E[i][j] = (i == j); T[i][j] = (i == j); }

    for (int k = 1; k <= 20; k++) {
        for (int i = 0; i < SD; i++)
            for (int j = 0; j < SD; j++) {
                double s = 0.0;
                for (int m = 0; m < SD; m++) s += T[i][m] * A[m][j] * sc;
                N[i][j] = s / k;
            }
        memcpy(T, N, sizeof T);
        for (int i = 0; i < SD; i++)
            for (int j = 0; j < SD; j++) E[i][j] += T[i][j];
    }
    for (int r = 0; r < sq; r++) {
        for (int i = 0; i < SD; i++)
            for (int j = 0; j < SD; j++) {
                double s = 0.0;
                for (int m = 0; m < SD; m++) s += E[i][m] * E[m][j];
                N[i][j] = s;
            }
        memcpy(E, N, sizeof(double) * SD * SD);
    }
}

/* ── ptol.c's Dirichlet projection, kept complex ─────────────────────── */
/* J_red  (k = 0-3, 8-11) cos channel;  J_blue (k = 4-7, 12-15) sin channel. */
static void project_complex(const unsigned char *s, int n, double sig,
                            double re[SD], double im[SD])
{
    for (int k = 0; k < SD; k++) {
        double freq = 2.0 * M_PI / (double)P[k];
        double cr = 0.0, ci = 0.0;
        for (int i = 1; i <= n; i++) {
            double ph = freq * (double)i;
            double w  = pow((double)i, -sig) * (double)s[i - 1];
            cr += w * cos(ph);
            ci += w * sin(ph);
        }
        re[k] = cr;  im[k] = ci;      /* z_k = re + i*im, phase RETAINED */
    }
}

/* ── the report ──────────────────────────────────────────────────────── */
static int rel(const char *name, const char *claim, int holds, const char *detail)
{
    printf("[%s] %-26s %s\n", holds ? "  ok" : "FAULT", name, claim);
    if (detail && *detail) printf("            %s\n", detail);
    return holds ? 0 : 1;
}

int main(int argc, char *argv[])
{
    const char *prompt = (argc > 1) ? argv[1] : "gravity defines down";
    char buf[256];

    g_tty = isatty(1);
    cd_build();

    /* the verified unit zero divisor: a = (e1 + e10)/sqrt2, strut 3 */
    double a[SD] = {0};
    a[1] = a[10] = 1.0 / sqrt(2.0);

    double L[SD][SD], M[SD][SD], W[SD][SD], w[SD], V[SD][SD], E[SD][SD];
    build_L(a, L);

    puts("======================================================================");
    puts("rotary_rerun — gravity in box kite space");
    puts("======================================================================\n");

    int faults = 0;

    /* 1. skew-symmetry: no strain, no shear, anywhere */
    double sn = sym_norm(L);
    snprintf(buf, sizeof buf, "||sym(L_a)|| = %.3e  -- no strain, so no shear", sn);
    faults += rel("zd.skew_symmetric", "L_a is exactly skew-symmetric", sn < TOL, buf);

    /* 2. spectrum: eigenvalues of L^T L give the gains squared */
    for (int i = 0; i < SD; i++)
        for (int j = 0; j < SD; j++) {
            double s = 0.0;
            for (int k = 0; k < SD; k++) s += L[k][i] * L[k][j];
            M[i][j] = s;
        }
    memcpy(W, M, sizeof W);
    jacobi(W, w, V);

    int n0 = 0, n1 = 0, n2 = 0;
    for (int i = 0; i < SD; i++) {
        double g = sqrt(fabs(w[i]) < 1e-14 ? 0.0 : w[i]);
        if (g < 1e-6)              n0++;
        else if (fabs(g - 1.0) < 1e-6)        n1++;
        else if (fabs(g - sqrt(2.0)) < 1e-6)  n2++;
    }
    snprintf(buf, sizeof buf, "gains 0 x%d, 1 x%d, sqrt2 x%d  -- bounded, discrete", n0, n1, n2);
    faults += rel("zd.spectrum", "the gains are 0 x4, 1 x8, sqrt2 x4",
                  n0 == 4 && n1 == 8 && n2 == 4, buf);

    double law = 0.0 * n0 + 1.0 * n1 + 2.0 * n2;
    snprintf(buf, sizeof buf, "0^2*%d + 1^2*%d + (sqrt2)^2*%d = %.0f -- the split is FORCED",
             n0, n1, n2, law);
    faults += rel("zd.counting_law", "sum gain^2 x multiplicity = 16", fabs(law - 16.0) < TOL, buf);

    /* 3. the kernel is the axis, and it is where DOWN does not exist */
    snprintf(buf, sizeof buf,
             "%d fixed dimensions, %d turning in %d planes. gain 0 = weightless:",
             n0, n1 + n2, (n1 + n2) / 2);
    faults += rel("gravity.kernel_is_axis", "the kernel is the AXIS of rotation", n0 == 4, buf);
    puts("            no direction there costs work, so no direction is DOWN.");
    puts("            and it does not ORBIT -- so it is gravity ABSENT, not free fall.");
    puts("            orbits are the global discriminant that breaks local equivalence.");

    /* 4. exp(L) is orthogonal: the flow is isometric, forever */
    mat_exp(L, E);
    double dev = 0.0;
    for (int i = 0; i < SD; i++)
        for (int j = 0; j < SD; j++) {
            double s = 0.0;
            for (int k = 0; k < SD; k++) s += E[k][i] * E[k][j];
            double t = s - (i == j ? 1.0 : 0.0);
            dev += t * t;
        }
    dev = sqrt(dev);
    snprintf(buf, sizeof buf, "||Q^T Q - I|| = %.3e  -- in SO(16). norm conserved for ALL t", dev);
    faults += rel("gravity.isometric", "exp(L_a) is orthogonal", dev < 1e-9, buf);

    /* 5. the torus: two frequencies, irrational ratio, dense orbit */
    int distinct = (n0 ? 0 : 0) + (n1 ? 1 : 0) + (n2 ? 1 : 0);
    snprintf(buf, sizeof buf,
             "T^%d, not T^%d. ratio 1 : sqrt2 = %.9f is IRRATIONAL",
             distinct, (n1 + n2) / 2, sqrt(2.0));
    faults += rel("gravity.toroidal", "the orbit closes on a 2-torus", distinct == 2, buf);
    puts("            incommensurate -> the orbit is DENSE and quasiperiodic.");
    puts("            never repeats, never leaves. the stable spot is an ORBIT,");
    puts("            not a point -- it comes arbitrarily close, infinitely often.");

    /* 6. the Noether information current -- and why sigma_self cannot see it */
    double re[SD], im[SD];
    project_complex((const unsigned char *)prompt, (int)strlen(prompt), 0.5, re, im);

    double p_red = 0.0, p_blue = 0.0;
    for (int k = 0; k < SD; k++) {
        int blue = (k >= 4 && k <= 7) || (k >= 12 && k <= 15);
        double pw = re[k] * re[k] + im[k] * im[k];
        if (blue) p_blue += pw; else p_red += pw;
    }
    double sigma = (p_red + p_blue > 0) ? p_red / (p_red + p_blue) : NAN;

    /* j ~ Im(z* dz) across adjacent shells. ENTIRELY phase: a real
     * amplitude gives zero current, which is why a power ratio cannot
     * see it. */
    double jcur = 0.0;
    for (int k = 0; k + 1 < SD; k++) {
        double dr = re[k + 1] - re[k], di = im[k + 1] - im[k];
        jcur += re[k] * di - im[k] * dr;          /* Im(conj(z_k) * dz) */
    }

    /* temperature: the spread of shell power. hot = much at stake. */
    double pmin = 1e300, pmax = -1e300;
    for (int k = 0; k < SD; k++) {
        double pw = re[k] * re[k] + im[k] * im[k];
        if (pw < pmin) pmin = pw;
        if (pw > pmax) pmax = pw;
    }
    double temp = (pmax > 0) ? (pmax - pmin) / pmax : 0.0;
    int hot = temp > 0.5;
    int wet = fabs(jcur) > 1.0;

    puts("");
    printf("%s  WHITE  \u2654  input  %s  %s%s%s\n",
           WHITE, RST, DIM, prompt, RST);
    printf("        %sasks. white moves first -- the question opens the board.%s\n",
           DIM, RST);
    puts("");
    printf("%s  BLACK  \u265a  response  %s\n", BLACK, RST);
    printf("        sigma_self       %s%.9f%s   %s|z|^2 ratio -- phase already gone%s\n",
           DIM, sigma, RST, DIM, RST);
    printf("        Noether current  %s%+.6e%s   %sIm(z* dz) -- entirely phase%s\n",
           wet ? WET : DRY, jcur, RST, DIM, RST);
    printf("        temperature      %s%.6f%s\n", hot ? HOT : COLD, temp, RST);
    puts("");
    printf("        state   %s%s%s  %s%s%s\n",
           hot ? HOT : COLD, hot ? "HOT  forced, no deviation affordable"
                                 : "COLD slack exists, style is affordable", RST,
           wet ? WET : DRY, wet ? " / WET  the current is flowing"
                                : " / DRY  no current -- a real amplitude has none", RST);
    puts("");
    printf("        %sthe current is a VECTOR: it points.%s\n", DIM, RST);
    printf("        %sthe ratio is a scalar: it sits. that is the whole difference.%s\n", DIM, RST);

    puts("");
    puts("----------------------------------------------------------------------");
    printf("%s\n", faults ? "FAULTS PRESENT" : "all relations hold");
    puts("gravity defines DOWN: the direction that needs no justification.");
    puts("every other heading must be paid for, so every other heading is intention.");
    return faults ? 1 : 0;
}
