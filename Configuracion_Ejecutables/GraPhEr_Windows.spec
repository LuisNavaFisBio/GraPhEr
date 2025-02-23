# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['GraPhEr_ArchivoPrincipal.py'],
    pathex=[],
    binaries=[],
    datas=[('plasTeX', 'plasTeX'), ('Iconos', 'Iconos'), ('Carga', 'Carga')],
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
    name='GraPhEr_Ejecutable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    uac_admin=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Iconos\\IconoGraPhEr.ico',
)