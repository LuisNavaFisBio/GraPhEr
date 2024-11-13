# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['PantallaInicialInterfaz.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Edgar\\AppData\\Roaming\\Python\\Python312\\site-packages\\plasTeX', 'plasTeX'), ('Iconos', 'Iconos'), ('Carga', 'Carga')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GraPhEr',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Iconos\\IconoGraPhEr.ico',
)
