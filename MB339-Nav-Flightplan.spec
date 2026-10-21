# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\zorzi\\Desktop\\Github EddiZor\\flight-sim\\MB339-Nav-Flightplan\\main.py'],
    pathex=[],
    binaries=[('C:\\Users\\zorzi\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\SimConnect\\SimConnect.dll', 'SimConnect')],
    datas=[('C:\\Users\\zorzi\\Desktop\\Github EddiZor\\flight-sim\\MB339-Nav-Flightplan\\gps_icon.ico', '.'), ('C:\\Users\\zorzi\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\SimConnect\\SimConnect.dll', 'SimConnect')],
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
    name='MB339-Nav-Flightplan',
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
    icon=['C:\\Users\\zorzi\\Desktop\\Github EddiZor\\flight-sim\\MB339-Nav-Flightplan\\gps_icon.ico'],
)
