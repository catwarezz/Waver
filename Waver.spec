# -*- mode: python ; coding: utf-8 -*-
# Waver v1.1.0 PyInstaller Specification (Simplified)

# Basic data files
datas = [
    ('music', 'music'),
    ('UI_Photos', 'UI_Photos'),
    ('ffmpeg_bin/bin', 'ffmpeg_bin/bin'),
    ('ffmpeg_bin/doc', 'ffmpeg_bin/doc'),
    ('ffmpeg_bin/presets', 'ffmpeg_bin/presets'),
    ('ffmpeg_bin/LICENSE', 'ffmpeg_bin/'),
    ('ffmpeg_bin/README.txt', 'ffmpeg_bin/'),
    ('README.md', '.'),
    ('CHANGELOG.md', '.'),
    ('RELEASE_v1.1.0.md', '.'),
    ('VERSION', '.'),
    ('requirements.txt', '.'),
]

# Essential hidden imports
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtMultimedia',
    'librosa',
    'numpy',
    'scipy',
    'yt_dlp',
    'packaging',
    'certifi',
    'urllib3',
    'requests',
    'numba',
    'joblib',
    'soundfile',
    'resampy',
    'pooch',
    'lazy_loader',
    'soxr',
]

# Analysis
a = Analysis(
    ['Waver.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'PIL',
        'pandas',
        'sklearn',
        'jupyter',
        'IPython',
        'pytest',
        'sphinx',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Waver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon='UI_Photos/favicon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Waver_v1.1.0',
) 