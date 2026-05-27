/*
 * auth_totp.h — Holcus TOTP authentication interface
 *
 * RFC 6238 (TOTP) over RFC 4226 (HOTP) with SHA-1.
 * Compatible with Google Authenticator, Authy, any TOTP app.
 *
 * Enrollment QR: tools/holcus_totp_enroll.png  (scan once, discard)
 * Secret file:   auth_totp_secret.h             (gitignored, local only)
 *
 * Usage:
 *   #include "auth_totp.h"
 *   if (!auth_totp_verify("123456")) { deny(); }
 */

#ifndef HOLCUS_AUTH_TOTP_H
#define HOLCUS_AUTH_TOTP_H

/*
 * auth_totp_verify — validate a 6-digit TOTP code.
 *
 * Checks the current 30-second window plus ±1 window for clock drift.
 * Returns 1 if valid, 0 if invalid or malformed.
 */
int auth_totp_verify(const char *six_digit_code);

/*
 * auth_totp_current — return the current valid code (for testing only).
 * Do not expose this in production CLI output.
 */
unsigned int auth_totp_current(void);

#endif /* HOLCUS_AUTH_TOTP_H */
