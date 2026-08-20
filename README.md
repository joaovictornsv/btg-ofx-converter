# btg-ofx-converter

Convert **BTG Pactual** bank exports to **OFX** — for importing into personal finance apps (Quicken, GNUCash, etc.).

Runs entirely on your machine. No account data is uploaded anywhere.

## Summary

- [Privacy](#privacy)
- [What it does](#what-it-does)
- [Limitations](#limitations)
- [Report issues / feedback](#report-issues--feedback)
- [Recommended folder (especially for non-developers)](#recommended-folder-especially-for-non-developers)
- [Guia em português](#guia-em-português)
- [Quick start (download — no Python)](#quick-start-download--no-python)
- [Exporting from BTG](#exporting-from-btg)
- [Quick start (from source)](#quick-start-from-source)
- [Development](#development)
- [License](#license)

## Privacy

- **Everything runs locally** — your extratos and faturas never leave your computer.
- **Do not commit** real `.xls`, `.xlsx`, or generated `.ofx` files to git or share them publicly.
- This repository contains **no real account data** — only synthetic examples under `examples/`.

## What it does

Two commands, two BTG export types:

| Command | Input | Output |
| ------- | ----- | ------ |
| `checking` | Checking-account `.xls` extrato | `{name}.ofx` |
| `card` | Credit card `.xlsx` fatura | `{name}.ofx` |

Tested only with **BTG Pactual** export formats. Not affiliated with BTG.

## Limitations

- **Checking:** legacy `.xls` extrato de conta corrente — not `.xlsx`.
- **Card:** `.xlsx` fatura de cartão — not the checking extrato format.
- BTG may change export layouts; if conversion fails after a BTG update, [open an issue](#report-issues--feedback).
- Credit card OFX uses `ACCTTYPE=CREDITCARD` inside a standard bank OFX envelope. Some apps may expect a different credit-card OFX layout.

## Report issues / feedback

If something does not work or BTG changed their export format:

- Open a [GitHub Issue](https://github.com/joaovictornsv/btg-ofx-converter/issues)
- Or email [hi@joaovictornsv.dev](mailto:hi@joaovictornsv.dev)

## Recommended folder (especially for non-developers)

Create a **dedicated folder** for BTG exports and the converter — not mixed with Downloads.

**Put in that folder:**

- The downloaded **program** (`btg-ofx-converter.exe` on Windows, or `btg-ofx-converter-macos-arm64` / `btg-ofx-converter-linux-x86_64`)
- Your BTG **extrato** (`.xls`) and/or **fatura** (`.xlsx`) files
- The generated **`.ofx`** files (created next to each input file)

**Example layout:**

```text
btg-ofx/                              ← your dedicated folder
├── btg-ofx-converter-macos-arm64     ← program (or .exe on Windows)
├── Extrato_2026-01.xls               ← BTG checking export
├── extrato.ofx                       ← generated
├── 2026-08-15_Fatura_BTG.xlsx        ← BTG card fatura
├── fatura.ofx                        ← generated (same stem as input)
└── guia-btg-ofx.md                   ← usage guide (copied here on first run)
```

Open the terminal **inside** this folder before running commands.

## Guia em português

Step-by-step instructions in Portuguese: **[docs/guia-btg-ofx.md](docs/guia-btg-ofx.md)** — readable directly on GitHub.

## Quick start (download — no Python)

1. Create your folder and download the program from **[Releases](https://github.com/joaovictornsv/btg-ofx-converter/releases)**:
   - **Windows:** `btg-ofx-converter-windows-x86_64` → rename to `btg-ofx-converter.exe` (optional)
   - **macOS (Apple Silicon):** `btg-ofx-converter-macos-arm64`
   - **Linux:** `btg-ofx-converter-linux-x86_64`
2. Read the [Portuguese guide](docs/guia-btg-ofx.md) (also copied to your folder on first run).
3. Export your file from BTG (see [Exporting from BTG](#exporting-from-btg)).
4. Run the matching command:

**Checking account (`.xls`)**

```bash
./btg-ofx-converter-macos-arm64 checking Extrato_2026-01.xls
```

**Credit card fatura (`.xlsx`)**

```bash
./btg-ofx-converter-macos-arm64 card 2026-08-15_Fatura_BTG.xlsx
```

5. Import the generated `.ofx` into your finance app.

**macOS:** first run may show a Gatekeeper warning (unsigned binary). Use **System Settings → Privacy & Security → Open Anyway**, or run once: `xattr -cr ./btg-ofx-converter-macos-arm64`.

**No internet required** — conversion is fully offline.

## Exporting from BTG

### Checking account — extrato (`.xls`)

1. Open the BTG app or website and go to your **conta corrente**.
2. Export or download the **extrato** for the desired period.
3. Confirm the file extension is **`.xls`** (Excel 97–2003), not `.xlsx`.
4. Run `checking` with the file path.

### Credit card — fatura (`.xlsx`)

1. Open the BTG app or website and go to **cartão de crédito**.
2. Download the **fatura** for the desired cycle (often named like `YYYY-MM-DD_Fatura_BTG.xlsx`).
3. Confirm the extension is **`.xlsx`**.
4. Run `card` with the file path.

## Quick start (from source)

### Requirements

- Python 3.10+
- `xlrd` (`.xls`) and `openpyxl` (`.xlsx`)

### Installation

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

### Run tests

```bash
python -m unittest discover -s tests -v
```

## Development

Maintainers: tag `v*` to trigger GitHub Actions release builds.

```bash
./scripts/build-binary.sh
```

See [PLAN.md](PLAN.md) for architecture and release details.

## License

[MIT](LICENSE)
