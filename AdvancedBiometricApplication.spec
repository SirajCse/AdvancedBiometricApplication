# -*- mode: python ; coding: utf-8 -*-


block_cipher = pyi_crypto.PyiBlockCipher(key='QWERTYUIOP12345678')


a = Analysis(
    ['src\\main.py'],
    pathex=['src', 'src/core', 'src/utils', 'src/biometric'],
    binaries=[],
    datas=[('config', 'config'), ('data', 'data'), ('scripts', 'scripts')],
    hiddenimports=['sqlite3', 'requests', 'urllib3', 'logging.handlers'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['custom_runtime.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name='AdvancedBiometricApplication',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
