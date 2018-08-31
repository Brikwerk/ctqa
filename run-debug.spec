# -*- mode: python -*-

block_cipher = None

options = [ 
    ('--onefile', None, 'OPTION'),
    ('--windowed', None, 'OPTION')
]

a = Analysis(['run.py'],
             binaries=[],
             datas=[
                 ('res/*', 'res'),
                 ('test/data/*', 'test/data')
                ],
             hiddenimports=[],
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
          options,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='run',
          debug=True,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True,
          icon='res/ctqa-icon.ico' )

app = BUNDLE(exe,
         name='CTQA.app',
         icon='res/ctqa-icon.icns',
         bundle_identifier=None,
         info_plist={
            'NSHighResolutionCapable': 'True'
            }
         )
