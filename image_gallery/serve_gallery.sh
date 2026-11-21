#!/bin/bash
# Open the VAPMIP Gallery through a local web server on 127.0.0.1 (Firefox shows the favicon only for http pages). Serves the repository root so the image links resolve.
# Usage: ./serve_gallery.sh [port=8772]   (loopback only; stop with: pkill -f "http.server 8772")
cd "$(dirname "$0")/.."; PORT=${1:-8772}
curl -s -o /dev/null "http://127.0.0.1:$PORT/image_gallery/favicon.png" || { nohup python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 & sleep 1; }
xdg-open "http://127.0.0.1:$PORT/image_gallery/VAPMIP_Gallery.html" >/dev/null 2>&1
