/*
 * PtolC/daemon.c — Ptolemy daemon mode.
 *
 * The monad is loaded once and kept resident (165 MB is negligible).
 * Connections are handled sequentially — the monad is not thread-safe
 * and does not need to be; query latency is sub-millisecond.
 *
 * Systemd socket activation: if $LISTEN_FDS >= 1 the kernel has already
 * bound the socket and passed it as fd 3.  We skip bind()/listen() and
 * use fd 3 directly.  No libsystemd dependency.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>

#include "ptolemy.h"
#include "monad.h"
#include "state.h"
#include "log.h"
#include "daemon.h"
#include "search.h"
#include "sensor.h"
#include "code.h"

/* ── Signal handling ──────────────────────────────────────────────────────── */

static volatile int g_quit = 0;

static void handle_sig(int sig)
{
    (void)sig;
    g_quit = 1;
}

/* ── Socket path resolution ───────────────────────────────────────────────── */

const char *daemon_sock_path(const char *flag_path, const char *ptolemy_dir)
{
    static char resolved[4096];

    if (flag_path && flag_path[0]) {
        snprintf(resolved, sizeof(resolved), "%s", flag_path);
        return resolved;
    }
    const char *env = getenv("PTOLEMY_SOCKET");
    if (env && env[0]) {
        snprintf(resolved, sizeof(resolved), "%s", env);
        return resolved;
    }
    if (ptolemy_dir && ptolemy_dir[0])
        snprintf(resolved, sizeof(resolved), "%s/ptolemy.sock", ptolemy_dir);
    else
        snprintf(resolved, sizeof(resolved), ".ptolemy.sock");
    return resolved;
}

/* ── PID file ─────────────────────────────────────────────────────────────── */

static void pid_write(const char *pid_path)
{
    FILE *f = fopen(pid_path, "w");
    if (!f) return;
    fprintf(f, "%d\n", (int)getpid());
    fclose(f);
}

static void pid_remove(const char *pid_path)
{
    if (pid_path) unlink(pid_path);
}

/* ── Client handler ───────────────────────────────────────────────────────── */

static void handle_client(Monad *m, int fd, int verbose)
{
    /* Wrap fd in FILE* for line-oriented I/O */
    FILE *in  = fdopen(dup(fd), "r");
    FILE *out = fdopen(dup(fd), "w");
    if (!in || !out) {
        if (in)  fclose(in);
        if (out) fclose(out);
        return;
    }

    char line[4096];
    while (fgets(line, sizeof(line), in)) {
        /* strip trailing \r\n */
        size_t l = strlen(line);
        while (l > 0 && (line[l-1] == '\n' || line[l-1] == '\r'))
            line[--l] = '\0';

        if (strncmp(line, "HEAR ", 5) == 0) {
            const char *query = line + 5;
            plog(PLOG_INFO, "daemon HEAR: %s", query);
            char *resp = monad_speak(m, query, 50, verbose);
            fprintf(out, "%s\n.\n", resp);
            fflush(out);
            free(resp);
            monad_self_flush(m);

        } else if (strcmp(line, "STATUS") == 0) {
            monad_status(m, out);
            fprintf(out, ".\n");
            fflush(out);

        } else if (strcmp(line, "HEALTH") == 0) {
            monad_health(m, out);
            fprintf(out, ".\n");
            fflush(out);

        } else if (strcmp(line, "QUIT") == 0) {
            fprintf(out, "OK\n.\n");
            fflush(out);
            break;

        } else if (strncmp(line, "SEARCH ", 7) == 0) {
            /* SEARCH <query>  — context search: arXiv + Wikipedia */
            const char *query = line + 7;
            plog(PLOG_INFO, "daemon SEARCH: %s", query);
            PtolSearchResult results[PTOL_SEARCH_MAX];
            double zeros[8];
            int nz = 0;
            int n = ptol_search_context(query, results, PTOL_SEARCH_MAX,
                                        zeros, &nz);
            for (int i = 0; i < n; i++) {
                fprintf(out, "[%s] %s\n%s\n",
                        results[i].source == PTOL_SEARCH_ARXIV ? "arxiv" : "wiki",
                        results[i].title, results[i].summary);
                /* Feed title+summary into field */
                char combined[1024];
                snprintf(combined, sizeof(combined), "%s %s",
                         results[i].title, results[i].summary);
                monad_learn(m, combined, 1.0f);
            }
            if (nz > 0) {
                fprintf(out, "[lmfdb] zeros:");
                for (int i = 0; i < nz; i++)
                    fprintf(out, " %.4f", zeros[i]);
                fprintf(out, "\n");
            }
            fprintf(out, ".\n");
            fflush(out);

        } else if (strcmp(line, "SENSOR_READ") == 0) {
            /* SENSOR_READ  — read 8 sensor channels from live_state.json */
            plog(PLOG_INFO, "daemon SENSOR_READ");
            float ch[8];
            sensor_read(ch, NULL);
            sensor_print(ch, out);
            /* Feed dominant channel name into field */
            int top = 0;
            for (int i = 1; i < 8; i++)
                if (ch[i] > ch[top]) top = i;
            static const char *CH_NAMES[8] = {
                "identity","negate","bind","name",
                "apply","abstract","branch","iterate"};
            monad_learn(m, CH_NAMES[top], 0);
            fprintf(out, ".\n");
            fflush(out);

        } else if (strncmp(line, "CODE_READ ", 10) == 0) {
            /* CODE_READ <path>  — profile a source file */
            const char *path = line + 10;
            plog(PLOG_INFO, "daemon CODE_READ: %s", path);
            CodeProfile prof;
            if (code_read_file(path, &prof)) {
                code_profile_print(&prof, out);
                /* Feed file into field via monad_learn on first 256 chars */
                FILE *src = fopen(path, "r");
                if (src) {
                    char snippet[256];
                    size_t got = fread(snippet, 1, 255, src);
                    fclose(src);
                    snippet[got] = '\0';
                    monad_learn(m, snippet, 1.0f);
                }
            } else {
                fprintf(out, "ERR cannot read %s\n", path);
            }
            fprintf(out, ".\n");
            fflush(out);

        } else if (l > 0) {
            fprintf(out, "ERR unknown command\n.\n");
            fflush(out);
        }
    }

    fclose(in);
    fclose(out);
}

/* ── Server ───────────────────────────────────────────────────────────────── */

int daemon_serve(Monad *m, const char *sock_path, const char *ckpt_path,
                 const char *pid_path, int verbose)
{
    int server_fd = -1;

    /* Check for systemd socket activation ($LISTEN_FDS set by systemd) */
    const char *listen_fds_str = getenv("LISTEN_FDS");
    if (listen_fds_str && atoi(listen_fds_str) >= 1) {
        server_fd = 3;   /* SD_LISTEN_FDS_START */
        plog(PLOG_INFO, "daemon using systemd-activated socket (fd %d)", server_fd);
    } else {
        /* Create and bind our own socket */
        server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
        if (server_fd < 0) {
            plog(PLOG_ERROR, "daemon socket(): %s", strerror(errno));
            return -1;
        }

        struct sockaddr_un addr;
        memset(&addr, 0, sizeof(addr));
        addr.sun_family = AF_UNIX;
        strncpy(addr.sun_path, sock_path, sizeof(addr.sun_path) - 1);

        unlink(sock_path);   /* remove stale socket if present */

        if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
            plog(PLOG_ERROR, "daemon bind(%s): %s", sock_path, strerror(errno));
            close(server_fd);
            return -1;
        }
        chmod(sock_path, 0600);

        if (listen(server_fd, 16) < 0) {
            plog(PLOG_ERROR, "daemon listen(): %s", strerror(errno));
            close(server_fd);
            return -1;
        }
        plog(PLOG_INFO, "daemon listening on %s", sock_path);
    }

    /* PID file */
    if (pid_path) pid_write(pid_path);

    /* Signal handlers */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_sig;
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT,  &sa, NULL);

    /* Serve loop */
    while (!g_quit) {
        int client = accept(server_fd, NULL, NULL);
        if (client < 0) {
            if (errno == EINTR) continue;   /* signal received — check g_quit */
            if (!g_quit)
                plog(PLOG_WARN, "daemon accept(): %s", strerror(errno));
            break;
        }
        handle_client(m, client, verbose);
        close(client);
    }

    plog(PLOG_INFO, "daemon shutting down");

    if (ckpt_path) {
        plog(PLOG_INFO, "daemon saving checkpoint %s", ckpt_path);
        state_save(m, ckpt_path, 0.0);
    }

    close(server_fd);
    if (listen_fds_str == NULL) unlink(sock_path);
    pid_remove(pid_path);
    return 0;
}

/* ── Client ───────────────────────────────────────────────────────────────── */

static int client_connect(const char *sock_path)
{
    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) {
        fprintf(stderr, "[ptolemy] socket(): %s\n", strerror(errno));
        return -1;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, sock_path, sizeof(addr.sun_path) - 1);

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        fprintf(stderr, "[ptolemy] cannot connect to daemon at %s: %s\n",
                sock_path, strerror(errno));
        close(fd);
        return -1;
    }
    return fd;
}

/* Read lines from fd until ".\n" sentinel, printing each to stdout. */
static void client_read_response(int fd)
{
    FILE *f = fdopen(dup(fd), "r");
    if (!f) return;
    char line[4096];
    while (fgets(line, sizeof(line), f)) {
        if (strcmp(line, ".\n") == 0) break;
        fputs(line, stdout);
    }
    fclose(f);
}

int daemon_query(const char *query, const char *sock_path)
{
    int fd = client_connect(sock_path);
    if (fd < 0) return -1;

    dprintf(fd, "HEAR %s\n", query);
    client_read_response(fd);
    dprintf(fd, "QUIT\n");
    close(fd);
    return 0;
}

int daemon_command(const char *cmd, const char *sock_path)
{
    int fd = client_connect(sock_path);
    if (fd < 0) return -1;

    dprintf(fd, "%s\n", cmd);
    client_read_response(fd);
    dprintf(fd, "QUIT\n");
    close(fd);
    return 0;
}
