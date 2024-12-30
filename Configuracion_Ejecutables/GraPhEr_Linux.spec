# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['GraPhEr_ArchivoPrincipal.py'],
             pathex=[],
             binaries=[],
             datas=[('C:\\Users\\Edgar\\AppData\\Roaming\\Python\\Python312\\site-packages\\plasTeX', 'plasTeX'), ('Iconos', 'Iconos'), ('Carga', 'Carga')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.datas,
          [],
          exclude_binaries=True,
          name='GraPhEr',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='Iconos\\IconoGraPhEr.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='GraPhEr',
               icon='Iconos\\IconoGraPhEr.ico')
