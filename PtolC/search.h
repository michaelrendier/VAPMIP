/*
 * PtolC/search.h — Live context search declarations.
 */

#ifndef PTOL_SEARCH_H
#define PTOL_SEARCH_H

#define PTOL_SEARCH_MAX   16
#define PTOL_TITLE_MAX   256
#define PTOL_SUMMARY_MAX 768

typedef enum {
    PTOL_SEARCH_ARXIV = 0,
    PTOL_SEARCH_WIKI  = 1,
    PTOL_SEARCH_S2    = 2,
    PTOL_SEARCH_LMFDB = 3,
} PtolSearchSource;

typedef struct {
    PtolSearchSource source;
    char title[PTOL_TITLE_MAX];
    char summary[PTOL_SUMMARY_MAX];
} PtolSearchResult;

/*
 * ptol_cepstrum_gate - P5 adversarial text check. Returns 1=pass, 0=blocked.
 */
int ptol_cepstrum_gate(const char *text);

/*
 * ptol_search_arxiv - Search arXiv, fill results[0..max_results-1].
 * Returns number of results filled.
 */
int ptol_search_arxiv(const char *query, PtolSearchResult *results,
                      int max_results);

/*
 * ptol_search_wiki - Fetch Wikipedia page summary into result.
 * Returns 1 on success, 0 on failure.
 */
int ptol_search_wiki(const char *query, PtolSearchResult *result);

/*
 * ptol_search_lmfdb - Fetch Riemann zeros into zeros_out[0..max_zeros-1].
 * Returns number of zeros filled (falls back to first 8 known zeros).
 */
int ptol_search_lmfdb(double *zeros_out, int max_zeros);

/*
 * ptol_search_context - Combined arXiv + Wikipedia + LMFDB.
 * Returns total result count. zeros_out/n_zeros_out may be NULL.
 */
int ptol_search_context(const char *query,
                        PtolSearchResult *results, int max_results,
                        double *zeros_out, int *n_zeros_out);

#endif /* PTOL_SEARCH_H */
