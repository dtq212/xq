# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\ACER\\PycharmProjects\\xq\\trochoi.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\ACER\\PycharmProjects\\xq\\_internal\\hdsd', 'hdsd/'), ('C:\\Users\\ACER\\PycharmProjects\\xq\\_internal\\amthanh', 'amthanh/'), ('C:\\Users\\ACER\\PycharmProjects\\xq\\_internal\\icon', 'icon/'), ('C:\\Users\\ACER\\PycharmProjects\\xq\\_internal\\log', 'log/')],
    hiddenimports=['pkg_resources'],
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
    [],
    exclude_binaries=True,
    name='trochoi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon=['C:\\Users\\ACER\\PycharmProjects\\xq\\_internal\\icon\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='trochoi',
)
