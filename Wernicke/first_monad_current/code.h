/*
 * PtolC/code.h — Source file cognition declarations.
 */

#ifndef PTOL_CODE_H
#define PTOL_CODE_H

#include <stdio.h>

/* Lower-𝕆 dimension indices */
#define CODE_DIM_IDENTITY  0
#define CODE_DIM_NEGATE    1
#define CODE_DIM_BIND      2
#define CODE_DIM_NAME      3
#define CODE_DIM_APPLY     4
#define CODE_DIM_ABSTRACT  5
#define CODE_DIM_BRANCH    6
#define CODE_DIM_ITERATE   7

#define CODE_PATH_MAX 4096

typedef struct {
    char path[CODE_PATH_MAX];
    int  counts[8];       /* raw keyword/token counts per dim */
    int  dominant_dim;    /* e₁..e₇ with highest count */
} CodeProfile;

/*
 * code_read_file - Read source file and fill CodeProfile.
 * Returns 1 on success, 0 on failure.
 */
int code_read_file(const char *path, CodeProfile *profile);

/*
 * code_profile_to_vec - Normalise profile counts to 8-float unit vector.
 * vec8 must point to float[8].
 */
void code_profile_to_vec(const CodeProfile *profile, float *vec8);

/*
 * code_profile_print - Print human-readable profile table to out.
 */
void code_profile_print(const CodeProfile *profile, FILE *out);

#endif /* PTOL_CODE_H */
