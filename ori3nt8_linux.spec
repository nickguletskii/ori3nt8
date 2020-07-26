# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['ori3nt8/gui/main.py'],
             pathex=['/home/nick/PycharmProjects/ori3nt8'],
             binaries=[],
             datas=[('resources/network.onnx', 'resources'), ('resources/ori3nt8.svg', 'resources'),
                    ('resources/license_rollup.txt', 'resources'), ('resources/version_tag.txt', 'resources'),],
             hiddenimports=["_struct", "zlib"],
             hookspath=[],
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
          [],
          exclude_binaries=True,
          name='ori3nt8',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ori3nt8')
