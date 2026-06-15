/*
 * ptol.c — Sedenion geometry engine.
 *
 * usage: ptol [-r] [-s [dir]] [-b [dir]] [-H [dir]] [-i <image>] <prompt>
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
 *   -r         raw mode: 16 scalars + primes, machine-readable
 *   -s [dir]   write SVG paper (pathway — spiral from ZD to great circle)
 *   -b [dir]   write PPM bitmap paper (field — 16 scalar amplitudes)
 *   -H [dir]   write HTML paper (SVG + bitmap + text shadow, all together)
 *   -i <file>  read image as prompt (via ImageMagick — geometry-first OCR)
 *
 * Papers are written to dir (default: current directory).
 * Filename: ptol_<prompt_slug>_<timestamp>.{svg,ppm,html}
 *
 * SVG: 16-spoke web showing sedenion field. Spiral path from ZD (centre)
 *      outward to great circle (rim), tracing the Lagrangian trajectory.
 *      Active prime spokes highlighted. Sign encoded by colour (red/blue).
 *
 * PPM: 4×4 grid of pixels, one per sedenion dimension.
 *      Brightness = |x_k|, hue = sign (red positive, blue negative).
 *      Upscaled to 256×256 nearest-neighbour for visibility.
 *
 * HTML: SVG + PPM (as data URI) + text shadow (spiral words placeholder).
 *
 * OCR emergence: -i reads the image geometry via ImageMagick, samples it
 *   to 16 scalars (one per sedenion dimension), and feeds those as the
 *   prompt geometry. When the geometry matches what is in the Zero Lattice
 *   the word emerges without pattern matching. Geometry-first, not pixel-first.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <sys/stat.h>
#include "ptolemy.h"

/* Directory containing the ptol binary (and ptol_layer.py). Set in main(). */
static char g_ptol_dir[512] = ".";

static const int P[16] = {
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53
};

/* Sedenion basis angles: 16 spokes evenly around the unit circle. */
static double spoke_angle(int k)
{
    return 2.0 * M_PI * (double)k / 16.0 - M_PI / 2.0;
}

/* ── Dirichlet projection ────────────────────────────────────────────────── */

static double project(const unsigned char *s, int n, int k)
{
    double sum  = 0.0;
    double freq = 2.0 * M_PI / (double)P[k];
    for (int i = 1; i <= n; i++)
        sum += (double)s[i-1] * pow((double)i, -0.5) * cos(freq * (double)i);
    return sum;
}

/* ── Comparator (ascending |x|, for spiral ZD→great circle) ─────────────── */

static int cmp_mag_asc(const void *a, const void *b)
{
    const int *ia = (const int *)a, *ib = (const int *)b;
    extern double _x[16];
    double da = fabs(_x[*ia]), db = fabs(_x[*ib]);
    return (da > db) - (da < db);
}

double _x[16];

/* ── Filename slug from prompt ───────────────────────────────────────────── */

static void make_slug(const char *prompt, char *slug, size_t sz)
{
    size_t j = 0;
    int words = 0;
    const char *p = prompt;
    while (*p && j < sz - 1 && words < 5) {
        if (*p == ' ' || *p == '\t') {
            if (j > 0 && slug[j-1] != '_') {
                slug[j++] = '_';
                words++;
            }
        } else if ((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z') ||
                   (*p >= '0' && *p <= '9') || *p == '-') {
            slug[j++] = (char)(*p | 0x20); /* lowercase */
        }
        p++;
    }
    while (j > 0 && slug[j-1] == '_') j--;
    slug[j] = '\0';
    if (j == 0) { strncpy(slug, "ptol", sz); slug[sz-1] = '\0'; }
}

static void make_outpath(const char *dir, const char *slug, long ts,
                         const char *ext, char *out, size_t sz)
{
    if (dir && *dir)
        snprintf(out, sz, "%s/ptol_%s_%ld.%s", dir, slug, ts, ext);
    else
        snprintf(out, sz, "ptol_%s_%ld.%s", slug, ts, ext);
}

/* ── Monad layer — call ptol_layer.py, get element name + one word per dim ── */
/*
 * Writes normalised scalars + active primes to a tempfile, calls:
 *   python3 ptol_layer.py --stdin --words-only < tmpfile
 * Reads back: line 0 = element name (the monad that fired, e.g. "English"),
 *             lines 1..16 = one word per dimension k=0..15.
 * layer_elem receives the element name for the SVG <ElementName> tag.
 * On any failure words are zero-initialised and layer_elem is "English".
 */

static void get_monad_words(const double *v, const double *raw_x,
                             double thresh_raw,
                             char words[16][256], char layer_elem[64])
{
    strncpy(layer_elem, "English", 63); layer_elem[63] = '\0';

    char tmp[] = "/tmp/ptol_words_XXXXXX";
    int  fd    = mkstemp(tmp);
    if (fd < 0) return;

    FILE *tf = fdopen(fd, "w");
    if (!tf) { close(fd); return; }
    for (int k = 0; k < 16; k++)
        fprintf(tf, "%+.10f\n", v[k]);
    fprintf(tf, "---\n");
    for (int k = 0; k < 16; k++)
        if (fabs(raw_x[k]) >= thresh_raw)
            fprintf(tf, "%d\n", P[k]);
    fclose(tf);

    char cmd[1024];
    snprintf(cmd, sizeof(cmd),
        "python3 '%s/ptol_layer.py' --stdin --words-only < '%s' 2>/dev/null",
        g_ptol_dir, tmp);

    FILE *pipe = popen(cmd, "r");
    if (pipe) {
        /* Line 0: element name */
        char elem_line[64];
        if (fgets(elem_line, sizeof(elem_line), pipe)) {
            int l = (int)strlen(elem_line);
            if (l > 0 && elem_line[l-1] == '\n') elem_line[l-1] = '\0';
            if (elem_line[0] >= 'A' && elem_line[0] <= 'Z')
                strncpy(layer_elem, elem_line, 63);
        }
        /* Lines 1-16: words */
        for (int k = 0; k < 16; k++) {
            if (!fgets(words[k], 256, pipe)) break;
            int l = (int)strlen(words[k]);
            if (l > 0 && words[k][l-1] == '\n') words[k][l-1] = '\0';
        }
        pclose(pipe);
    }
    remove(tmp);
}

/* ── SVG paper — the pathway ─────────────────────────────────────────────── */
/*
 * 16-spoke polar web. Each spoke k points at spoke_angle(k).
 * Radius of tip = |v[k]| × R_max.   Sign: red (+), blue (−).
 * Spiral path: connect tips in ascending |x| order (ZD → great circle).
 * Active prime spokes (|x_k| >= thresh) drawn bold.
 *
 * <English> operator: for active spokes, emit a bare <English> XML element
 * at the amplitude dot position — no fill, no definition. monad_English.bin
 * is the source; the geometry decides whether it fires. The SVG source IS
 * the architecture. The render is the shadow.
 */

static int write_svg(const char *path, const double *v, const int *idx,
                     double thresh_norm, const char *prompt,
                     const char words[16][256], const char *layer_elem)
{
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); return 0; }

    const int W = 500, H = 520;
    const double CX = 250.0, CY = 260.0, R = 210.0;

    fprintf(f, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    fprintf(f, "<svg xmlns=\"http://www.w3.org/2000/svg\" "
               "width=\"%d\" height=\"%d\" viewBox=\"0 0 %d %d\">\n", W, H, W, H);

    /* Background */
    fprintf(f, "  <rect width=\"%d\" height=\"%d\" fill=\"#0a0a0a\"/>\n", W, H);

    /* Prompt label */
    char safe[256];
    size_t si = 0;
    for (const char *p = prompt; *p && si < sizeof(safe)-5; p++) {
        if (*p == '<') { memcpy(safe+si, "&lt;", 4); si+=4; }
        else if (*p == '>') { memcpy(safe+si, "&gt;", 4); si+=4; }
        else if (*p == '&') { memcpy(safe+si, "&amp;", 5); si+=5; }
        else safe[si++] = *p;
    }
    safe[si] = '\0';
    fprintf(f, "  <text x=\"%d\" y=\"16\" font-family=\"monospace\" "
               "font-size=\"11\" fill=\"#444\" text-anchor=\"middle\">%s</text>\n",
               W/2, safe);

    /* Concentric reference circles at R/4, R/2, 3R/4, R */
    for (int r = 1; r <= 4; r++) {
        fprintf(f, "  <circle cx=\"%.1f\" cy=\"%.1f\" r=\"%.1f\" "
                   "fill=\"none\" stroke=\"#222\" stroke-width=\"0.5\"/>\n",
                   CX, CY, R * r / 4.0);
    }

    /* σ=½ circle (the escape threshold) — at R/2 */
    fprintf(f, "  <circle cx=\"%.1f\" cy=\"%.1f\" r=\"%.1f\" "
               "fill=\"none\" stroke=\"#2a4a2a\" stroke-width=\"1\" "
               "stroke-dasharray=\"4,4\"/>\n", CX, CY, R * 0.5);
    fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
               "font-size=\"8\" fill=\"#2a4a2a\" text-anchor=\"start\">"
               "σ=½</text>\n", CX + R*0.5 + 2, CY);

    /* Spokes, amplitude dots, and English word labels */
    for (int k = 0; k < 16; k++) {
        double a    = spoke_angle(k);
        double tip_r = fabs(v[k]) * R;
        double tx   = CX + cos(a) * R;
        double ty   = CY + sin(a) * R;
        int active  = (fabs(v[k]) >= thresh_norm);

        /* Spoke line */
        fprintf(f, "  <line x1=\"%.2f\" y1=\"%.2f\" x2=\"%.2f\" y2=\"%.2f\" "
                   "stroke=\"%s\" stroke-width=\"%.1f\"/>\n",
                   CX, CY, tx, ty,
                   active ? "#333" : "#1a1a1a",
                   active ? 0.8 : 0.4);

        /* Amplitude dot */
        if (tip_r > 1.0) {
            double dx = CX + cos(a) * tip_r;
            double dy = CY + sin(a) * tip_r;
            const char *col = (v[k] >= 0) ? "#c04040" : "#4060c0";
            fprintf(f, "  <circle cx=\"%.2f\" cy=\"%.2f\" r=\"%.1f\" "
                       "fill=\"%s\" opacity=\"0.9\"/>\n",
                       dx, dy, active ? 4.0 : 2.5, col);
        }

        /* English word at spoke tip — the shadow on the wall of primes */
        const char *word = words ? words[k] : NULL;
        char wsvg[64]; wsvg[0] = '\0';
        if (word && word[0]) {
            /* Truncate + XML-escape for SVG */
            int wi = 0;
            const char *wp = word;
            int chars = 0;
            while (*wp && chars < 13 && wi < 58) {
                if      (*wp == '<') { memcpy(wsvg+wi,"&lt;",4); wi+=4; }
                else if (*wp == '>') { memcpy(wsvg+wi,"&gt;",4); wi+=4; }
                else if (*wp == '&') { memcpy(wsvg+wi,"&amp;",5); wi+=5; }
                else                 wsvg[wi++] = *wp;
                chars++; wp++;
            }
            if (*wp) { memcpy(wsvg+wi,"…",3); wi+=3; } /* UTF-8 ellipsis */
            wsvg[wi] = '\0';

            double lx = CX + cos(a) * (R + 16);
            double ly = CY + sin(a) * (R + 16);
            if (active) {
                /* Active: green word — the path lands here */
                fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
                           "font-size=\"10\" fill=\"#40a060\" font-weight=\"bold\" "
                           "text-anchor=\"middle\" dominant-baseline=\"central\">"
                           "%s</text>\n", lx, ly, wsvg);
            } else {
                /* Inactive: dim word — present but below threshold */
                fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
                           "font-size=\"8\" fill=\"#2a2a2a\" "
                           "text-anchor=\"middle\" dominant-baseline=\"central\">"
                           "%s</text>\n", lx, ly, wsvg);
            }
        } else {
            /* No word: fall back to prime label */
            double lx = CX + cos(a) * (R + 14);
            double ly = CY + sin(a) * (R + 14);
            fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
                       "font-size=\"9\" fill=\"%s\" text-anchor=\"middle\" "
                       "dominant-baseline=\"central\">p%d</text>\n",
                       lx, ly, active ? "#666" : "#2a2a2a", P[k]);
        }

        /* <Monad> element — bare XML at amplitude dot. No fill. No definition.
         * Element name = the monad that fired. The geometry chose it. */
        if (active && word && word[0] && tip_r > 1.0) {
            double ex = CX + cos(a) * tip_r;
            double ey = CY + sin(a) * tip_r;
            fprintf(f, "  <%s x=\"%.2f\" y=\"%.2f\">%s</%s>\n",
                       layer_elem, ex, ey, wsvg, layer_elem);
        }
    }

    /* Spiral path: connect tips in ZD→great circle order */
    fprintf(f, "  <polyline fill=\"none\" stroke=\"#40a060\" "
               "stroke-width=\"1.2\" opacity=\"0.8\" points=\"");
    /* Start at centre (ZD) */
    fprintf(f, "%.2f,%.2f", CX, CY);
    for (int i = 0; i < 16; i++) {
        int k = idx[i];
        double a = spoke_angle(k);
        double r = fabs(v[k]) * R;
        fprintf(f, " %.2f,%.2f", CX + cos(a)*r, CY + sin(a)*r);
    }
    fprintf(f, "\"/>\n");

    /* ZD marker (centre) */
    fprintf(f, "  <circle cx=\"%.1f\" cy=\"%.1f\" r=\"3\" "
               "fill=\"#806020\" opacity=\"0.9\"/>\n", CX, CY);
    fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
               "font-size=\"8\" fill=\"#806020\" text-anchor=\"middle\">ZD</text>\n",
               CX, CY + 12);

    /* e_k labels at amplitude tips (inner, readable) */
    for (int k = 0; k < 16; k++) {
        double a = spoke_angle(k);
        double r = fabs(v[k]) * R;
        if (r < 8.0) continue;
        double lx = CX + cos(a) * (r * 0.6);
        double ly = CY + sin(a) * (r * 0.6);
        fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
                   "font-size=\"7\" fill=\"#555\" text-anchor=\"middle\" "
                   "dominant-baseline=\"central\">e%d</text>\n", lx, ly, k);
    }

    fprintf(f, "</svg>\n");
    fclose(f);
    return 1;
}

/* ── PPM bitmap paper — the field ────────────────────────────────────────── */
/*
 * 4×4 grid (16 cells), one per sedenion dimension k.
 * Cell layout: k=0 top-left, row-major.
 * R channel: positive amplitude   (v[k] > 0)
 * B channel: negative amplitude   (v[k] < 0)
 * G channel: activity (above threshold)
 * Upscaled ×16 to 64×64 by nearest-neighbour.
 */

#define PPM_CELL  16
#define PPM_GRID   4
#define PPM_SZ    (PPM_CELL * PPM_GRID)

static int write_ppm(const char *path, const double *v, double thresh_norm)
{
    unsigned char img[PPM_SZ][PPM_SZ][3];
    memset(img, 0, sizeof(img));

    for (int k = 0; k < 16; k++) {
        int row = k / PPM_GRID;
        int col = k % PPM_GRID;
        int py0 = row * PPM_CELL, px0 = col * PPM_CELL;
        double amp = fabs(v[k]);
        int bright = (int)(amp * 255.0 + 0.5);
        if (bright > 255) bright = 255;
        int active = (amp >= thresh_norm);

        unsigned char R = (v[k] >= 0) ? (unsigned char)bright : 0;
        unsigned char B = (v[k] <  0) ? (unsigned char)bright : 0;
        unsigned char G = active ? (unsigned char)(bright / 3) : 0;

        for (int dy = 1; dy < PPM_CELL-1; dy++)
            for (int dx = 1; dx < PPM_CELL-1; dx++) {
                img[py0+dy][px0+dx][0] = R;
                img[py0+dy][px0+dx][1] = G;
                img[py0+dy][px0+dx][2] = B;
            }
        /* Cell border */
        for (int d = 0; d < PPM_CELL; d++) {
            img[py0][px0+d][0] = img[py0][px0+d][1] = img[py0][px0+d][2] = 0x18;
            img[py0+PPM_CELL-1][px0+d][0] = img[py0+PPM_CELL-1][px0+d][1] =
                img[py0+PPM_CELL-1][px0+d][2] = 0x18;
            img[py0+d][px0][0] = img[py0+d][px0][1] = img[py0+d][px0][2] = 0x18;
            img[py0+d][px0+PPM_CELL-1][0] = img[py0+d][px0+PPM_CELL-1][1] =
                img[py0+d][px0+PPM_CELL-1][2] = 0x18;
        }
    }

    FILE *f = fopen(path, "wb");
    if (!f) { perror(path); return 0; }
    fprintf(f, "P6\n%d %d\n255\n", PPM_SZ, PPM_SZ);
    for (int y = 0; y < PPM_SZ; y++)
        for (int x = 0; x < PPM_SZ; x++)
            fwrite(img[y][x], 1, 3, f);
    fclose(f);
    return 1;
}

/* ── HTML paper — pathway + field + shadow text ──────────────────────────── */

static int write_html(const char *html_path, const char *svg_path,
                      const char *ppm_path, const double *v, const int *idx,
                      const int *P16, double thresh_norm, const char *prompt,
                      const char words[16][256])
{
    /* Convert PPM to PNG via ImageMagick if available, embed SVG inline. */
    char png_path[512];
    snprintf(png_path, sizeof(png_path), "%.507s.png", ppm_path);
    char cmd[2048];
    snprintf(cmd, sizeof(cmd), "convert '%.500s' '%.500s' 2>/dev/null", ppm_path, png_path);
    if (system(cmd)) { /* ImageMagick PNG conversion optional */ }

    FILE *f = fopen(html_path, "w");
    if (!f) { perror(html_path); return 0; }

    fprintf(f, "<!DOCTYPE html><html><head>\n");
    fprintf(f, "<meta charset=\"UTF-8\">\n");
    fprintf(f, "<title>ptol: %s</title>\n", prompt);
    fprintf(f, "<style>\n"
               "body{background:#0a0a0a;color:#aaa;font-family:monospace;"
               "max-width:900px;margin:2em auto;padding:1em}\n"
               "h1{font-size:1em;color:#555;font-weight:normal}\n"
               ".papers{display:flex;gap:2em;align-items:flex-start}\n"
               ".paper{border:1px solid #222;padding:0.5em}\n"
               ".paper p{font-size:0.7em;color:#333;margin:0.3em 0 0}\n"
               ".shadow{margin-top:2em;border-top:1px solid #222;padding-top:1em}\n"
               ".spiral{color:#40a060;letter-spacing:0.05em}\n"
               "table{border-collapse:collapse;font-size:0.8em}\n"
               "td{padding:2px 6px;border:1px solid #1a1a1a}\n"
               ".pos{color:#c04040}.neg{color:#4060c0}.act{font-weight:bold}\n"
               "</style></head><body>\n");

    fprintf(f, "<h1>σ: %s</h1>\n", prompt);
    fprintf(f, "<div class=\"papers\">\n");

    /* SVG paper (inline — read the SVG file) */
    fprintf(f, "  <div class=\"paper\">\n");
    FILE *svgf = fopen(svg_path, "r");
    if (svgf) {
        char buf[4096]; size_t nr;
        while ((nr = fread(buf, 1, sizeof(buf), svgf)) > 0)
            fwrite(buf, 1, nr, f);
        fclose(svgf);
    } else {
        fprintf(f, "  <p>[SVG not found]</p>\n");
    }
    fprintf(f, "  <p>pathway — spiral ZD → great circle</p>\n");
    fprintf(f, "  </div>\n");

    /* PPM/PNG paper */
    fprintf(f, "  <div class=\"paper\">\n");
    /* Try PNG first, fall back to nothing */
    fprintf(f, "  <img src=\"%s\" width=\"128\" height=\"128\" "
               "style=\"image-rendering:pixelated\" alt=\"sedenion field\">\n",
               png_path);
    fprintf(f, "  <p>field — 16 scalar amplitudes<br>"
               "red=+, blue=−, green=active</p>\n");
    fprintf(f, "  </div>\n");
    fprintf(f, "</div>\n");

    /* Sedenion table with English words */
    fprintf(f, "<div class=\"shadow\">\n");
    fprintf(f, "<table><tr><th>k</th><th>p_k</th><th>e_k</th>"
               "<th>scalar</th><th>active</th><th>word</th></tr>\n");
    for (int k = 0; k < 16; k++) {
        int active = (fabs(v[k]) >= thresh_norm);
        const char *cls = (v[k] >= 0) ? "pos" : "neg";
        if (active) cls = "act";
        const char *word = (words && words[k][0]) ? words[k] : "";
        fprintf(f, "<tr><td>%d</td><td>%d</td>"
                   "<td class=\"%s\">e%d</td>"
                   "<td class=\"%s\">%+.6f</td>"
                   "<td>%s</td>"
                   "<td class=\"%s\">%s</td></tr>\n",
                   k, P16[k], cls, k, cls, v[k],
                   active ? "●" : "",
                   active ? "act" : "", word);
    }
    fprintf(f, "</table>\n");

    /* Spiral path with English words */
    fprintf(f, "<p class=\"spiral\">path (ZD → great circle):<br>");
    const char *last_word = NULL;
    for (int i = 0; i < 16; i++) {
        int k = idx[i];
        int active = (fabs(v[k]) >= thresh_norm);
        const char *word = (words && words[k][0]) ? words[k] : NULL;
        if (word) {
            if (active)
                fprintf(f, "<strong style=\"color:#40a060\">%s</strong>", word);
            else
                fprintf(f, "<span style=\"color:#444\">%s</span>", word);
            if (i < 15) fprintf(f, " → ");
            last_word = words[k];
        } else {
            fprintf(f, "e%d(%+.3f)%s", k, v[k], i < 15 ? " → " : "");
        }
    }
    fprintf(f, "</p>\n");

    /* Response: the word the path lands at */
    if (last_word && last_word[0]) {
        fprintf(f, "<p style=\"font-size:1.4em;color:#40a060;"
                   "border-left:2px solid #40a060;padding-left:0.8em;"
                   "margin-top:1em\">%s</p>\n", last_word);
    }

    fprintf(f, "</div>\n</body></html>\n");

    fclose(f);
    return 1;
}

/* ── Image reading — geometry-first OCR ─────────────────────────────────── */
/*
 * Use ImageMagick to resample the image to 16×1 pixels, then read each
 * pixel's brightness as a sedenion scalar. Sign is encoded by hue:
 * red-dominant → positive, blue-dominant → negative.
 *
 * When the geometry of the image matches what is in the Zero Lattice,
 * the word emerges. OCR without pattern matching — geometry recognition.
 */

static int read_image_scalars(const char *img_path, double *v_out)
{
    char cmd[2048];
    char tmpfile[] = "/tmp/ptol_ocr_XXXXXX";
    int fd = mkstemp(tmpfile);
    if (fd < 0) { perror("mkstemp"); return 0; }
    close(fd);

    /* Resample to 16×1, output as text RGB */
    snprintf(cmd, sizeof(cmd),
        "convert \"%s\" -colorspace sRGB -resize 16x1! -depth 8 "
        "-format \"%%[fx:p{%%[fx:i]}.u.r] %%[fx:p{%%[fx:i]}.u.g] "
        "%%[fx:p{%%[fx:i]}.u.b]\\n\" info:- 2>/dev/null > \"%s\"",
        img_path, tmpfile);

    /* Simpler: use txt: format */
    snprintf(cmd, sizeof(cmd),
        "convert \"%s\" -colorspace sRGB -resize 16x1! -depth 8 txt:- "
        "2>/dev/null | grep -v '#' > \"%s\"",
        img_path, tmpfile);

    if (system(cmd) != 0) {
        fprintf(stderr, "ptol: ImageMagick 'convert' failed on %s\n", img_path);
        fprintf(stderr, "ptol: install ImageMagick: sudo apt install imagemagick\n");
        remove(tmpfile);
        return 0;
    }

    FILE *tf = fopen(tmpfile, "r");
    if (!tf) { perror(tmpfile); remove(tmpfile); return 0; }

    char line[256];
    int k = 0;
    while (k < 16 && fgets(line, sizeof(line), tf)) {
        /* txt: format: "x,y: (R,G,B)  #RRGGBB  ..." */
        int r = 0, g = 0, b = 0;
        if (sscanf(line, "%*d,%*d: (%d,%d,%d)", &r, &g, &b) == 3 ||
            sscanf(line, "%*d,%*d: (%d,%d,%d,", &r, &g, &b) == 3) {
            double brightness = (r + g + b) / (3.0 * 255.0);
            /* Sign from hue: red-dominant → +, blue-dominant → − */
            double sign = (r >= b) ? 1.0 : -1.0;
            v_out[k] = sign * brightness;
            k++;
        }
    }
    fclose(tf);
    remove(tmpfile);

    if (k < 16) {
        fprintf(stderr, "ptol: only read %d scalars from image (need 16)\n", k);
        return 0;
    }
    return 1;
}

/* ── Main ────────────────────────────────────────────────────────────────── */

int main(int argc, char *argv[])
{
    /* Locate our own directory so get_english_words() can find ptol_layer.py */
    {
        char self[512];
        ssize_t len = readlink("/proc/self/exe", self, sizeof(self)-1);
        if (len > 0) {
            self[len] = '\0';
            char *slash = strrchr(self, '/');
            if (slash) { *slash = '\0'; g_ptol_dir[0]='\0'; strncat(g_ptol_dir, self, sizeof(g_ptol_dir)-1); }
        }
    }

    int raw       = 0;
    int do_svg    = 0;
    int do_bmp    = 0;
    int do_html   = 0;
    const char *out_dir   = "";
    const char *img_input = NULL;
    int arg0 = 1;

    while (arg0 < argc && argv[arg0][0] == '-') {
        if (strcmp(argv[arg0], "-r") == 0) {
            raw = 1; arg0++;
        } else if (strcmp(argv[arg0], "-s") == 0) {
            do_svg = 1; arg0++;
            if (arg0 < argc && (argv[arg0][0]=='.' || argv[arg0][0]=='/' || argv[arg0][0]=='~')) out_dir = argv[arg0++];
        } else if (strcmp(argv[arg0], "-b") == 0) {
            do_bmp = 1; arg0++;
            if (arg0 < argc && (argv[arg0][0]=='.' || argv[arg0][0]=='/' || argv[arg0][0]=='~')) out_dir = argv[arg0++];
        } else if (strcmp(argv[arg0], "-H") == 0) {
            do_svg = do_bmp = do_html = 1; arg0++;
            if (arg0 < argc && (argv[arg0][0]=='.' || argv[arg0][0]=='/' || argv[arg0][0]=='~')) out_dir = argv[arg0++];
        } else if (strcmp(argv[arg0], "-i") == 0) {
            arg0++;
            if (arg0 >= argc) { fprintf(stderr, "ptol: -i needs <image>\n"); return 1; }
            img_input = argv[arg0++];
        } else {
            break;
        }
    }

    double v[16];

    if (img_input) {
        /* ── Image read mode ── */
        if (!read_image_scalars(img_input, v)) return 1;
        /* v[] already normalised-ish from pixel range; re-normalise */
        double norm2 = 0.0;
        for (int k = 0; k < 16; k++) norm2 += v[k]*v[k];
        double norm = sqrt(norm2);
        if (norm > 0.0) for (int k = 0; k < 16; k++) v[k] /= norm;

        printf("image: %s\n", img_input);
        printf("geometry (from image):\n");
        for (int k = 0; k < 16; k++)
            printf("  e%-2d  %+.8f\n", k, v[k]);

        int idx[16];
        for (int k = 0; k < 16; k++) idx[k] = k;
        /* Sort ascending |v| for spiral */
        for (int i = 0; i < 15; i++)
            for (int j = i+1; j < 16; j++)
                if (fabs(v[idx[i]]) > fabs(v[idx[j]])) {
                    int t = idx[i]; idx[i] = idx[j]; idx[j] = t;
                }

        printf("\nspiral (ZD → great circle):\n  ");
        for (int i = 0; i < 16; i++)
            printf("e%d(%+.3f)%s", idx[i], v[idx[i]], i < 15 ? " → " : "\n");

        return 0;
    }

    /* ── Text prompt mode ── */
    char sigma[65536];
    sigma[0] = '\0';

    if (argc <= arg0) {
        /* No argument: try stdin if it's a pipe */
        if (isatty(STDIN_FILENO)) {
            fprintf(stderr,
                "usage: ptol [-r] [-s [dir]] [-b [dir]] [-H [dir]] [-i <img>] <prompt>\n");
            return 1;
        }
        size_t cap = sizeof(sigma) - 1;
        size_t len = 0;
        int c;
        while (len < cap && (c = getchar()) != EOF && c != '\n')
            sigma[len++] = (char)c;
        sigma[len] = '\0';
        /* strip trailing whitespace */
        while (len > 0 && (sigma[len-1] == ' ' || sigma[len-1] == '\r'))
            sigma[--len] = '\0';
        if (len == 0) {
            fprintf(stderr, "ptol: empty prompt\n");
            return 1;
        }
    } else {
        for (int i = arg0; i < argc; i++) {
            if (i > arg0) strncat(sigma, " ", sizeof(sigma) - strlen(sigma) - 1);
            strncat(sigma, argv[i], sizeof(sigma) - strlen(sigma) - 1);
        }
    }
    int n = (int)strlen(sigma);

    double norm = 0.0, peak = 0.0;
    for (int k = 0; k < 16; k++) {
        _x[k] = project((const unsigned char *)sigma, n, k);
        norm  += _x[k] * _x[k];
        if (fabs(_x[k]) > peak) peak = fabs(_x[k]);
    }
    norm = sqrt(norm);

    for (int k = 0; k < 16; k++)
        v[k] = (norm > 0.0) ? _x[k] / norm : 0.0;

    double thresh      = peak / MONAD_PHI;
    double thresh_norm = (norm > 0.0) ? thresh / norm : 0.0;

    int idx[16];
    for (int k = 0; k < 16; k++) idx[k] = k;
    qsort(idx, 16, sizeof(int), cmp_mag_asc);

    /* ── Monad layer (all non-raw modes) — math selects from full domain ── */
    char words[16][256];
    char layer_elem[64];
    memset(words, 0, sizeof(words));
    strncpy(layer_elem, "English", 63); layer_elem[63] = '\0';
    if (!raw)
        get_monad_words(v, _x, thresh, words, layer_elem);

    /* ── Papers dir (shared by default SVG and explicit flags) ── */
    static char ptolemy_papers[512];
    ptolemy_papers[0] = '\0';
    if (!out_dir || !*out_dir) {
        const char *home = getenv("HOME");
        if (home) {
            char ph[512];
            snprintf(ph, sizeof(ph), "%s/.ptolemy", home);
            mkdir(ph, 0755);
            snprintf(ptolemy_papers, sizeof(ptolemy_papers), "%s/.ptolemy/papers", home);
            mkdir(ptolemy_papers, 0755);
            out_dir = ptolemy_papers;
        }
    }

    char slug[64];
    make_slug(sigma, slug, sizeof(slug));
    long ts = (long)time(NULL);

    /* ── Default mode: SVG + English stdout ── */
    if (!raw && !do_svg && !do_bmp && !do_html) {
        char svg_path[1024];
        make_outpath(out_dir, slug, ts, "svg", svg_path, sizeof(svg_path));
        if (write_svg(svg_path, v, idx, thresh_norm, sigma, words, layer_elem))
            fprintf(stderr, "paper: %s\n", svg_path);

        /* English firing order (Riemann spiral) to stdout */
        for (int i = 0; i < 16; i++) {
            int k = idx[i];
            int active = (fabs(v[k]) >= thresh_norm);
            const char *w = words[k][0] ? words[k] : NULL;
            if (i > 0) printf(" ");
            if (active) printf("*");
            printf("%s", w ? w : "·");
        }
        printf("\n");
    }

    /* ── Raw mode ── */
    if (raw) {
        for (int k = 0; k < 16; k++)
            printf("%+.10f\n", v[k]);
        printf("---\n");
        for (int k = 0; k < 16; k++)
            if (fabs(_x[k]) >= thresh)
                printf("%d\n", P[k]);
    }

    /* ── Explicit paper output (-s / -b / -H) ── */
    if (do_svg || do_bmp || do_html) {
        char svg_path[1024], ppm_path[1024], html_path[1024];
        make_outpath(out_dir, slug, ts, "svg",  svg_path,  sizeof(svg_path));
        make_outpath(out_dir, slug, ts, "ppm",  ppm_path,  sizeof(ppm_path));
        make_outpath(out_dir, slug, ts, "html", html_path, sizeof(html_path));

        if (do_svg) {
            if (write_svg(svg_path, v, idx, thresh_norm, sigma, words, layer_elem))
                fprintf(stderr, "paper (pathway): %s\n", svg_path);
        }
        if (do_bmp) {
            if (write_ppm(ppm_path, v, thresh_norm))
                fprintf(stderr, "paper (field):   %s\n", ppm_path);
        }
        if (do_html) {
            if (write_html(html_path, svg_path, ppm_path,
                           v, idx, P, thresh_norm, sigma, words))
                fprintf(stderr, "paper (html):    %s\n", html_path);
        }
    }

    return 0;
}
