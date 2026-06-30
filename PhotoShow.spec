# -*- mode: python ; coding: utf-8 -*-
"""
PhotoShow PyInstaller Spec File
================================
This spec file configures PyInstaller to:
1. Bundle the application with all assets and data files
2. Include the .env file so Cloudinary credentials are available in production
3. Create a single-folder distribution for easier deployment
4. Include the application icon

Usage:
    pyinstaller PhotoShow.spec --clean --noconfirm

Note:
    The .env file is bundled into the executable folder. After building,
    verify that dist/PhotoShow/.env exists and contains your Cloudinary credentials.
"""

import os
from pathlib import Path

# Get the project root directory
project_root = Path(SPEC).parent

a = Analysis(
    [os.path.join(project_root, 'main.py')],
    pathex=[],
    binaries=[],
    datas=[
        # Bundle assets folder (fonts, images, icons)
        (os.path.join(project_root, 'app', 'assets'), 'app/assets'),
        # Bundle CSV seed data files
        (os.path.join(project_root, 'app', 'files'), 'app/files'),
        # NOTE: .env is NOT bundled here — build.py copies it to dist/PhotoShow/
        # after PyInstaller runs so it sits next to PhotoShow.exe, exactly where
        # main.py expects it (Path(sys.executable).parent / '.env').
    ],
    hiddenimports=[
        'dotenv',
        'cloudinary',
        'cloudinary.api',
        'cloudinary.uploader',
        'sqlalchemy',
        'PIL',
        'pillow_heif',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Required for onedir (COLLECT) builds
    name='PhotoShow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window on Windows
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'app', 'assets', 'PhotoShowIcon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PhotoShow',
    distpath=os.path.join(project_root, 'dist'),
    workpath=os.path.join(project_root, 'build'),
)
