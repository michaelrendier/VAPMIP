/*
 * dprint.h — Cody's dPrint() protocol for C: after a value changes, print its name and new value to stdout.
 * Ptolemy2/Phaleron/APISniff/APISniff.py:421 is the original (label = value, behind a global debug flag).  The flag is the environment
 * variable PTOL_DPRINT (unset or "0" = off; any other value = on).  Every line starts with "[dp] " so the feed can be grepped.
 * Unlike the original, a value of 0 or "" is printed as itself.
 */
#ifndef PTOL_DPRINT_H
#define PTOL_DPRINT_H
#include <stdio.h>
#include <stdlib.h>
static inline int ptol_dprint_on(void)
{
    static int on = -1;
    if (on < 0) { const char *e = getenv("PTOL_DPRINT"); on = (e && *e && *e != '0'); }
    return on;
}
#define DPRINT_S(name, val)  do { if (ptol_dprint_on()) printf("[dp] %s = \"%s\"\n", name, (val)); } while (0)
#define DPRINT_I(name, val)  do { if (ptol_dprint_on()) printf("[dp] %s = %ld\n", name, (long)(val)); } while (0)
#define DPRINT_D(name, val)  do { if (ptol_dprint_on()) printf("[dp] %s = %.17g\n", name, (double)(val)); } while (0)
#endif
