# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/codexrenderer/launcher.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/codexrenderer/assets', 'codexrenderer/assets'), ('src/codexrenderer/styles', 'codexrenderer/styles'), ('src/codexrenderer/thirdparty', 'codexrenderer/thirdparty')],
    hiddenimports=['codexrenderer.codexrenderer_gui', 'codexrenderer.geminirenderer_gui', 'codexrenderer.claudecode_gui', 'codexrenderer.gemini_cli', 'codexrenderer.claudecode_cli'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hooks/rt_tkdnd_env.py'],
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
    name='CodexRunner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
