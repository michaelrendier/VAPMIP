#!/usr/bin/env python3
"""
gen_totp_secret.py — regenerate TOTP secret and enrollment QR.

Run this ONCE to set up a new secret. It overwrites auth_totp_secret.h
and tools/holcus_totp_enroll.png.

INVALIDATES any existing Google Authenticator entry — remove the old
Ptolemy:Holcus entry from the app before scanning the new QR.

Usage:
    cd PtolemyHolcus/
    python3 tools/gen_totp_secret.py
"""

import os, base64, sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_H  = os.path.join(REPO_ROOT, "auth_totp_secret.h")
QR_PNG    = os.path.join(REPO_ROOT, "tools", "holcus_totp_enroll.png")

raw    = os.urandom(20)
b32    = base64.b32encode(raw).decode()
hex_arr = ', '.join(f'0x{b:02x}' for b in raw)

# Write C header
with open(SECRET_H, 'w') as f:
    f.write(f"""/*
 * auth_totp_secret.h — Holcus TOTP shared secret
 *
 * PRIVATE — do not commit. Listed in .gitignore.
 * Enrollment QR: tools/holcus_totp_enroll.png  (also gitignored)
 * B32 for manual entry: {b32}
 *
 * To regenerate (invalidates existing Authenticator entry):
 *   python3 tools/gen_totp_secret.py
 */

#ifndef HOLCUS_AUTH_TOTP_SECRET_H
#define HOLCUS_AUTH_TOTP_SECRET_H

static const unsigned char TOTP_SECRET_RAW[] = {{
    {hex_arr}
}};
static const int TOTP_SECRET_LEN = 20;

#endif /* HOLCUS_AUTH_TOTP_SECRET_H */
""")
print(f"Written: {SECRET_H}")

# Write QR PNG
try:
    import qrcode
    uri = (f"otpauth://totp/Ptolemy%3AHolcus"
           f"?secret={b32}&issuer=Ptolemy&algorithm=SHA1&digits=6&period=30")
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(QR_PNG)
    print(f"Written: {QR_PNG}")
    print(f"URI:     {uri}")
except ImportError:
    print("qrcode module not found — install with: pip install qrcode[pil]")
    print(f"Manual entry B32: {b32}")

print("\nNext steps:")
print("  1. Open Google Authenticator → + → Scan QR")
print(f"     QR image: {QR_PNG}")
print("  2. Or choose 'Enter a setup key' and paste the B32 above")
print("  3. Rebuild: make")
print("  4. Test:    make totp-test && ./totp_test")
