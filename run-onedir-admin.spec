# -*- mode: python -*-

block_cipher = None


a = Analysis(['run.py'],
             pathex=['R:\\CTQA-Dev'],
             binaries=[],
             datas=[
                 ('res/*', 'res'),
                 ('test/data/*', 'test/data')
                ],
             hiddenimports = [],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='CTQA',
          debug=True,
          strip=False,
          upx=True,
          console=True,
          icon='res/ctqa-icon.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='CTQA')

app = BUNDLE(exe,
         name='CTQA.app',
         icon='res/ctqa-icon.icns',
         bundle_identifier=None,
         info_plist={
            'NSHighResolutionCapable': 'True'
            }
         )
