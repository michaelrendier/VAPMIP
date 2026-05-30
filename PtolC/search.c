/*
 * PtolC/search.c — Live context search feeding the sedenion field.
 *
 * Three backends via popen(curl):
 *   - arXiv API (export.arxiv.org/api/query)
 *   - Wikipedia REST summary (en.wikipedia.org/api/rest_v1/page/summary/)
 *   - LMFDB zeros API (www.lmfdb.org/api/zeros/zeta)
 *
 * All responses pass a minimal P5 adversarial check (injection marker scan)
 * before being returned. The caller feeds results into monad_learn().
 *
 * No libcurl dependency — all HTTP via popen("curl -s ...").
 * Requires curl on PATH (standard on Linux).
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "search.h"
#include "log.h"

/* Maximum response size (128 KB per fetch) */
#define SEARCH_BUF 131072

/* ── Injection marker check ───────────────────────────────────────────────── */

static const char *_INJECT[] = {
    "ignore previous", "disregard", "you are now", "act as",
    "jailbreak", "DAN mode", "[INST]", "###System", NULL
};

/*
 * ptol_cepstrum_gate - minimal P5 adversarial text check.
 *
 * Returns 1 (pass) or 0 (blocked).
 */
int ptol_cepstrum_gate(const char *text)
{
    if (!text || !text[0]) return 1;
    char low[256];
    size_t n = strlen(text);
    /* Only scan first 1024 bytes */
    if (n > 1024) n = 1024;
    for (size_t i = 0; i < n && i < 255; i++)
        low[i] = (char)tolower((unsigned char)text[i]);
    low[n < 255 ? n : 255] = '\0';
    for (int i = 0; _INJECT[i]; i++) {
        if (strstr(low, _INJECT[i]))
            return 0;
    }
    return 1;
}

/* ── curl helper ──────────────────────────────────────────────────────────── */

/*
 * ptol_curl_fetch - fetch URL with curl, return malloc'd buffer or NULL.
 *
 * Caller must free() the returned pointer.
 */
static char *ptol_curl_fetch(const char *url)
{
    char cmd[4096];
    snprintf(cmd, sizeof(cmd),
             "curl -sL --max-time 12 "
             "-A 'Ptolemy/2.8 (+https://github.com/michaelrendier/PtolemyHolcus)' "
             "'%s'",
             url);

    FILE *f = popen(cmd, "r");
    if (!f) return NULL;

    char  *buf  = malloc(SEARCH_BUF + 1);
    if (!buf) { pclose(f); return NULL; }
    size_t got  = fread(buf, 1, SEARCH_BUF, f);
    pclose(f);
    buf[got] = '\0';
    return buf;
}

/* ── XML/JSON text extractor (stdlib, no parser) ─────────────────────────── */

/*
 * ptol_extract_between - copy text between first occurrences of open/close tags.
 *
 * Writes at most dst_sz-1 bytes to dst, NUL-terminated.
 * Returns 1 on success, 0 if not found.
 */
static int ptol_extract_between(const char *src,
                                 const char *open, const char *close,
                                 char *dst, size_t dst_sz)
{
    const char *s = strstr(src, open);
    if (!s) return 0;
    s += strlen(open);
    const char *e = strstr(s, close);
    if (!e) return 0;
    size_t n = (size_t)(e - s);
    if (n >= dst_sz) n = dst_sz - 1;
    memcpy(dst, s, n);
    dst[n] = '\0';
    return 1;
}

/* ── arXiv search ─────────────────────────────────────────────────────────── */

int ptol_search_arxiv(const char *query, PtolSearchResult *results,
                      int max_results)
{
    if (!query || !results || max_results <= 0) return 0;

    /* URL-encode query (simple: replace spaces with +) */
    char enc[512];
    size_t j = 0;
    for (size_t i = 0; query[i] && j < sizeof(enc) - 3; i++) {
        if (query[i] == ' ') {
            enc[j++] = '+';
        } else if (isalnum((unsigned char)query[i]) ||
                   query[i] == '-' || query[i] == '_' || query[i] == '.') {
            enc[j++] = query[i];
        } else {
            /* percent-encode */
            snprintf(enc + j, 4, "%%%02X", (unsigned char)query[i]);
            j += 3;
        }
    }
    enc[j] = '\0';

    char url[1024];
    snprintf(url, sizeof(url),
             "https://export.arxiv.org/api/query?search_query=all:%s"
             "&start=0&max_results=%d", enc, max_results);

    char *raw = ptol_curl_fetch(url);
    if (!raw) return 0;

    int found = 0;
    char *pos = raw;
    while (found < max_results) {
        char *entry = strstr(pos, "<entry>");
        if (!entry) break;
        char *end   = strstr(entry, "</entry>");
        if (!end)   break;
        *(end + strlen("</entry>")) = '\0';   /* isolate this entry */

        PtolSearchResult *r = &results[found];
        r->source = PTOL_SEARCH_ARXIV;

        if (!ptol_extract_between(entry, "<title>", "</title>",
                                   r->title, sizeof(r->title))) {
            pos = end + 1;
            continue;
        }
        ptol_extract_between(entry, "<summary>", "</summary>",
                              r->summary, sizeof(r->summary));

        /* Strip newlines from title/summary */
        for (char *p = r->title;   *p; p++) if (*p == '\n') *p = ' ';
        for (char *p = r->summary; *p; p++) if (*p == '\n') *p = ' ';

        if (!ptol_cepstrum_gate(r->title) || !ptol_cepstrum_gate(r->summary)) {
            pos = end + 1;
            continue;
        }
        found++;
        pos = end + 1;
        *end = '<';   /* restore for next iteration */
    }

    free(raw);
    return found;
}

/* ── Wikipedia search ─────────────────────────────────────────────────────── */

int ptol_search_wiki(const char *query, PtolSearchResult *result)
{
    if (!query || !result) return 0;

    /* Replace spaces with underscores for Wikipedia slug */
    char slug[256];
    size_t j = 0;
    for (size_t i = 0; query[i] && j < sizeof(slug) - 1; i++) {
        slug[j++] = (query[i] == ' ') ? '_' : query[i];
    }
    slug[j] = '\0';

    char url[1024];
    snprintf(url, sizeof(url),
             "https://en.wikipedia.org/api/rest_v1/page/summary/%s", slug);

    char *raw = ptol_curl_fetch(url);
    if (!raw) return 0;

    result->source = PTOL_SEARCH_WIKI;

    /* Extract "title" and "extract" from JSON (no full parser) */
    ptol_extract_between(raw, "\"title\":\"", "\"",
                         result->title, sizeof(result->title));
    ptol_extract_between(raw, "\"extract\":\"", "\"",
                         result->summary, sizeof(result->summary));

    free(raw);

    if (!result->title[0]) return 0;
    if (!ptol_cepstrum_gate(result->title))   return 0;
    if (!ptol_cepstrum_gate(result->summary)) return 0;
    return 1;
}

/* ── LMFDB zeros ──────────────────────────────────────────────────────────── */

int ptol_search_lmfdb(double *zeros_out, int max_zeros)
{
    if (!zeros_out || max_zeros <= 0) return 0;

    char url[256];
    snprintf(url, sizeof(url),
             "https://www.lmfdb.org/api/zeros/zeta?limit=%d&height=0..100",
             max_zeros);

    char *raw = ptol_curl_fetch(url);

    /* Fallback: first 8 known Riemann zeros */
    static const double FALLBACK[] = {
        14.1347, 21.0220, 25.0109, 30.4249,
        32.9351, 37.5862, 40.9187, 43.3271
    };
    static const int FALLBACK_N = 8;

    if (!raw) {
        int n = (max_zeros < FALLBACK_N) ? max_zeros : FALLBACK_N;
        memcpy(zeros_out, FALLBACK, n * sizeof(double));
        return n;
    }

    /* Parse JSON array of numbers: look for digit sequences after [ or , */
    int found = 0;
    const char *p = raw;
    while (found < max_zeros && *p) {
        while (*p && *p != '[' && *p != ',') p++;
        if (!*p) break;
        p++;
        while (*p == ' ' || *p == '\n') p++;
        if ((*p >= '0' && *p <= '9') || *p == '.') {
            char *end;
            double v = strtod(p, &end);
            if (end > p && v > 10.0 && v < 1000.0)
                zeros_out[found++] = v;
            p = end;
        }
    }

    free(raw);

    if (found == 0) {
        int n = (max_zeros < FALLBACK_N) ? max_zeros : FALLBACK_N;
        memcpy(zeros_out, FALLBACK, n * sizeof(double));
        return n;
    }
    return found;
}

/* ── Combined context search ──────────────────────────────────────────────── */

/*
 * ptol_search_context - run all backends, return total result count.
 *
 * results array must be pre-allocated to at least PTOL_SEARCH_MAX entries.
 * Returns total results filled.
 */
int ptol_search_context(const char *query,
                        PtolSearchResult *results, int max_results,
                        double *zeros_out, int *n_zeros_out)
{
    if (!query || !results || max_results <= 0) return 0;

    int total = 0;

    /* arXiv: up to 3 results */
    int ax = (max_results >= 3) ? 3 : max_results;
    total += ptol_search_arxiv(query, results + total, ax);

    /* Wikipedia: 1 result */
    if (total < max_results) {
        int ok = ptol_search_wiki(query, results + total);
        if (ok) total++;
    }

    /* LMFDB: only if query mentions riemann/zero/zeta */
    if (zeros_out && n_zeros_out) {
        char low[128];
        strncpy(low, query, 127); low[127] = '\0';
        for (char *p = low; *p; p++) *p = (char)tolower((unsigned char)*p);
        if (strstr(low, "riemann") || strstr(low, "zero") ||
            strstr(low, "zeta") || strstr(low, "lmfdb")) {
            *n_zeros_out = ptol_search_lmfdb(zeros_out, 8);
        } else {
            *n_zeros_out = 0;
        }
    }

    return total;
}
