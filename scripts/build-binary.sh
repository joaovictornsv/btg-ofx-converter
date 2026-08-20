#!/usr/bin/env bash
# Build a standalone btg-ofx-converter binary for the current OS/architecture.
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

.venv/bin/pip install -q -r requirements.txt pyinstaller
.venv/bin/pyinstaller --clean btg-ofx-converter.spec

echo ""
echo "Built: dist/btg-ofx-converter (or dist/btg-ofx-converter.exe on Windows)"
echo "Test:  dist/btg-ofx-converter checking examples/sample_extrato.xls"
echo "       dist/btg-ofx-converter card examples/sample_fatura.xlsx"
