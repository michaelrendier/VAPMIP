/*
 * PtolC/sensor.c — Physical sensor bridge: reads live_state.json.
 *
 * Maps 8 sensor channels (e₀..e₇, lower 𝕆 operator labels) from
 * ~/.ptolemy/live_state.json into a float vector for field ingestion.
 *
 * JSON format accepted:
 *   {"sensor": [v0, v1, v2, v3, v4, v5, v6, v7]}     (array form)
 *   {"sensor": {"identity": v, "negate": v, ...}}     (named form)
 *   {"sensor": {"0": v, "1": v, ...}}                 (index-string form)
 *
 * Channel → lower-𝕆 operator:
 *   0 identity  1 negate  2 bind  3 name
 *   4 apply     5 abstract  6 branch  7 iterate
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "sensor.h"
#include "log.h"

/* Default state file path (expanded at runtime) */
#define SENSOR_PATH_MAX 4096

static const char *CHANNEL_NAMES[8] = {
    "identity", "negate", "bind", "name",
    "apply", "abstract", "branch", "iterate"
};

/* ── Path resolution ──────────────────────────────────────────────────────── */

static void sensor_default_path(char *buf, size_t n)
{
    const char *home = getenv("HOME");
    if (!home) home = "/root";
    snprintf(buf, n, "%s/.ptolemy/live_state.json", home);
}

/* ── Minimal JSON float extractor ────────────────────────────────────────── */

/*
 * Find "key": value in a JSON string.
 * Returns 1 on success, 0 if not found.
 * For string keys, returns the numeric value following ":".
 */
static int json_get_float(const char *src, const char *key, double *out)
{
    char pat[64];
    snprintf(pat, sizeof(pat), "\"%s\":", key);
    const char *p = strstr(src, pat);
    if (!p) return 0;
    p += strlen(pat);
    while (*p == ' ' || *p == '\t') p++;
    char *end;
    double v = strtod(p, &end);
    if (end == p) return 0;
    *out = v;
    return 1;
}

/* ── Public API ───────────────────────────────────────────────────────────── */

int sensor_read(float *channels_out, const char *path)
{
    char default_path[SENSOR_PATH_MAX];
    if (!path || !path[0]) {
        sensor_default_path(default_path, sizeof(default_path));
        path = default_path;
    }

    for (int i = 0; i < 8; i++) channels_out[i] = 0.0f;

    FILE *f = fopen(path, "r");
    if (!f) {
        plog(PLOG_WARN, "sensor_read: cannot open %s", path);
        return 0;
    }

    /* Read entire file */
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (sz <= 0 || sz > 65536) { fclose(f); return 0; }

    char *buf = malloc((size_t)sz + 1);
    if (!buf) { fclose(f); return 0; }
    fread(buf, 1, (size_t)sz, f);
    fclose(f);
    buf[sz] = '\0';

    /* Locate "sensor" key */
    const char *sens = strstr(buf, "\"sensor\"");
    if (!sens) { free(buf); return 0; }
    sens += 8;   /* skip "sensor" */
    while (*sens == ':' || *sens == ' ') sens++;

    if (*sens == '[') {
        /* Array form: parse up to 8 floats */
        const char *p = sens + 1;
        for (int i = 0; i < 8; i++) {
            while (*p == ' ' || *p == ',') p++;
            if (*p == ']') break;
            char *end;
            double v = strtod(p, &end);
            if (end == p) break;
            channels_out[i] = (float)v;
            p = end;
        }
    } else if (*sens == '{') {
        /* Object form: named or index-string keys */
        for (int i = 0; i < 8; i++) {
            double v = 0.0;
            char idx[4];
            snprintf(idx, sizeof(idx), "%d", i);
            if (json_get_float(sens, CHANNEL_NAMES[i], &v) ||
                json_get_float(sens, idx, &v)) {
                channels_out[i] = (float)v;
            }
        }
    }

    free(buf);
    return 1;
}

int sensor_write(const float *channels, const char *path)
{
    char default_path[SENSOR_PATH_MAX];
    if (!path || !path[0]) {
        sensor_default_path(default_path, sizeof(default_path));
        path = default_path;
    }

    FILE *f = fopen(path, "w");
    if (!f) return 0;
    fprintf(f, "{\n  \"sensor\": {\n");
    for (int i = 0; i < 8; i++) {
        fprintf(f, "    \"%s\": %.6f%s\n",
                CHANNEL_NAMES[i], (double)channels[i],
                i < 7 ? "," : "");
    }
    fprintf(f, "  }\n}\n");
    fclose(f);
    return 1;
}

void sensor_print(const float *channels, FILE *out)
{
    /* L2 norm for callosum coupling proxy */
    double norm = 0.0;
    for (int i = 0; i < 8; i++)
        norm += (double)channels[i] * (double)channels[i];
    norm = sqrt(norm);

    fprintf(out, "sensor_channels:\n");
    for (int i = 0; i < 8; i++) {
        fprintf(out, "  e%-2d %-10s %.6f\n",
                i, CHANNEL_NAMES[i], (double)channels[i]);
    }
    fprintf(out, "  L2_norm %.6f\n", norm);
}
