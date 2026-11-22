#!/bin/sh
# Rewrite SemPriCon/requirements.txt from what is installed in SemPriCon/.venv right now. Run after any `pip install` there.
cd "$(dirname "$0")/.." || exit 1
.venv/bin/pip freeze > requirements.txt && echo "requirements.txt: $(wc -l < requirements.txt) packages"
