# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['ori3nt8\\gui\\main.py'],
             pathex=['specs/windows/'],
             binaries=[],
             datas=[('resources/network.onnx', 'resources'), ('resources/ori3nt8.svg', 'resources'), ('resources/ori3nt8.ico', 'resources')],
             hiddenimports=["_struct", "zlib"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

for d in a.datas:
    if '_C.cp37-win_amd64.pyd' in d[0]:
        a.datas.remove(d)
        break

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ori3nt8',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='resources\\ori3nt8.ico')