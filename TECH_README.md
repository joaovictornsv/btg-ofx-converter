# btg-ofx-converter — Technical documentation

Developer-facing notes. End users should read **[README.md](README.md)** (Portuguese, simplified).

---

## Overview

CLI tool that converts **BTG Pactual** bank exports to **OFX 1.x**:

| Subcommand | Input | Parser | `ACCTTYPE` |
| ---------- | ----- | ------ | ---------- |
| `checking` | Checking `.xls` extrato | `xls.py` | `CHECKING` |
| `card` | Credit card `.xlsx` fatura | `fatura.py` | `CREDITCARD` |

- **Entry point:** `convert.py` (also PyInstaller binary name `btg-ofx-converter`)
- **Architecture plan:** [PLAN.md](PLAN.md)
- **Portuguese user guide (GitHub):** [README.md](README.md) and [docs/guia-btg-ofx.md](docs/guia-btg-ofx.md)
- **Offline guide (binary):** `docs/guia-btg-ofx.html` — copied on first run; open in browser

Output: `{input_stem}.ofx` beside the input file. On first run, copies `guia-btg-ofx.html` to the same folder if missing.

---

## Setup

```bash
git clone https://github.com/joaovictornsv/btg-ofx-converter.git
cd btg-ofx-converter

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Try with sample files (no real data)

```bash
python convert.py checking examples/sample_extrato.xls
python convert.py card examples/sample_fatura.xlsx
```

Regenerate fixtures:

```bash
pip install xlwt
python scripts/generate-examples.py
```

---

## Project layout

```
convert.py              # CLI (checking + card)
guide.py                # Bundled guide copy on first run
xls.py                  # BTG checking .xls parser
fatura.py               # BTG card .xlsx parser
ofx.py                  # OFX read/write
models.py               # Transaction dataclass
examples/               # Synthetic BTG exports for tests/CI
docs/guia-btg-ofx.md    # GitHub pointer to README
docs/guia-btg-ofx.html  # Offline guide (bundled in binary; open in browser)
scripts/
  build-binary.sh
  generate-examples.py
tests/
btg-ofx-converter.spec  # PyInstaller
.github/workflows/
  test.yml
  release.yml
```

---

## Tests

```bash
python -m unittest discover -s tests -v
```

CI runs the same on push to `main`.

---

## Limitations

- **Checking:** legacy `.xls` extrato de conta corrente only — not `.xlsx`.
- **Card:** `.xlsx` fatura only — not checking extrato format.
- **Card password:** BTG fatura downloads are often password-protected (encrypted OLE2 disguised as `.xlsx`). `openpyxl` cannot read them. Users must decrypt and save an unprotected copy in Excel/LibreOffice before `card`.
- **OFX envelope:** v0.1.x uses `BANKMSGSRSV1` with `ACCTTYPE=CREDITCARD` for card — not `CREDITCARDMSGSRSV1` / `CCSTMTRS`. Some importers may reject this.
- Not affiliated with BTG; export layouts may change.
- macOS binaries are unsigned (Gatekeeper workaround documented in README).

---

## Exporting from BTG

### Checking — extrato (`.xls`)

1. BTG app/site → **conta corrente** → export extrato
2. Confirm extension `.xls` (Excel 97–2003)
3. `btg-ofx-converter checking path/to/extrato.xls`

### Card — fatura (`.xlsx`)

1. BTG app/site → **cartão de crédito** → download fatura
2. Open with BTG password → **Save As** without password
3. `btg-ofx-converter card path/to/fatura.xlsx`

---

## Building binaries

```bash
./scripts/build-binary.sh
# → dist/btg-ofx-converter (or .exe on Windows)
```

PyInstaller bundles `docs/guia-btg-ofx.html` via `btg-ofx-converter.spec`.

---

## Release

1. Bump / tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
2. GitHub Actions (`.github/workflows/release.yml`) builds linux / windows / macos
3. Smoke tests run both subcommands on `examples/*`
4. Artifacts: `btg-ofx-converter-{platform}` + `guia-btg-ofx.html`

---

## Privacy / security (technical)

- No network calls; no telemetry
- Parses local files only
- Do not commit real `.xls`, `.xlsx`, or `.ofx` user data (see `.gitignore`)

---

## Report issues

- [GitHub Issues](https://github.com/joaovictornsv/btg-ofx-converter/issues)
- [hi@joaovictornsv.dev](mailto:hi@joaovictornsv.dev)

---

## Screenshots for README

| File | Content |
| ---- | ------- |
| `01-download-release.png` | GitHub Releases — platform binaries highlighted |

Referenced from [README.md](README.md).

---

## License

[MIT](LICENSE)
