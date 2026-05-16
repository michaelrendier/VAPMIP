#!/usr/bin/env bash
# install_c_kernel.sh — install Jupyter and the C kernel for Ptolemy C notebooks
#
# Installs:
#   1. Jupyter Notebook (pip)
#   2. jupyter-c-kernel  — compiles and executes each notebook cell as C
#
# Usage:
#   chmod +x install_c_kernel.sh
#   ./install_c_kernel.sh
#
# After installation:
#   cd notebooks/c
#   jupyter notebook
#   Then select a *c.ipynb file and confirm the kernel is "C" (not Python).
#
# Requirements: Python 3.7+, pip, gcc

set -e

GRN='\033[0;32m'; RST='\033[0m'
info() { echo -e "${GRN}[install]${RST} $*"; }

# ── 1. Jupyter ─────────────────────────────────────────────────────────────────
info "Installing Jupyter Notebook..."
pip install --quiet --upgrade jupyter notebook

# ── 2. jupyter-c-kernel ────────────────────────────────────────────────────────
# Each notebook cell is compiled as a standalone C program and executed.
# No shared state between cells — each cell must include its own headers and main().
info "Installing jupyter-c-kernel..."
pip install --quiet jupyter-c-kernel

# ── 3. Register kernel with Jupyter ────────────────────────────────────────────
info "Registering C kernel with Jupyter..."
python -m jupyter_c_kernel.install

# ── 4. Verify ──────────────────────────────────────────────────────────────────
info "Installed kernels:"
jupyter kernelspec list

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  C kernel installed. Each notebook cell is a standalone C"
echo "  program compiled with gcc. All headers and main() required."
echo ""
echo "  Launch:"
echo "    cd notebooks/c"
echo "    jupyter notebook"
echo ""
echo "  Binary path: notebooks use ../../PtolC/ptolemy by default."
echo "  Build it first:  cd PtolC && make"
echo "══════════════════════════════════════════════════════════════"
