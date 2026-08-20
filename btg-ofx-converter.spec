# PyInstaller spec — build with: pyinstaller btg-ofx-converter.spec
# See scripts/build-binary.sh and .github/workflows/release.yml

block_cipher = None

a = Analysis(
    ["convert.py"],
    pathex=["."],
    binaries=[],
    datas=[("docs/guia-btg-ofx.html", "docs")],
    hiddenimports=[
        "xlrd",
        "openpyxl",
        "openpyxl.cell",
        "openpyxl.cell._writer",
        "openpyxl.workbook",
        "openpyxl.worksheet",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="btg-ofx-converter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
