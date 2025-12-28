"""
Build script to create standalone executable for Library Manager
Run: python build.py
"""
import subprocess
import shutil
import os
import sys
from pathlib import Path

BUILD_FOLDER = Path("MSF Library Manager")

def build():
    print("Building Library Manager...")
    
    # Create build folder
    BUILD_FOLDER.mkdir(exist_ok=True)
    
    # Run PyInstaller using python -m
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'library-manager',
        '--distpath', str(BUILD_FOLDER),
        '--workpath', 'build',
        '--specpath', '.',
        '--hidden-import=pandas',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("[OK] Executable created in " + str(BUILD_FOLDER) + "/")
    except subprocess.CalledProcessError as e:
        print("[FAILED] Build failed: " + str(e))
        return False
    
    # Create empty library.csv if it doesn't exist
    csv_path = BUILD_FOLDER / "library.csv"
    if not csv_path.exists():
        with open(csv_path, 'w') as f:
            f.write("ISBN;Title;Author;Publisher;Year;Signature;Description;Keywords\n")
        print("[OK] Created " + str(csv_path))
    
    # Cleanup build artifacts
    if Path('build').exists():
        shutil.rmtree('build')
    if Path('library-manager.spec').exists():
        Path('library-manager.spec').unlink()
    
    print("\n[OK] Build complete! Folder: " + str(BUILD_FOLDER) + "/")
    print("  To run: Open '" + str(BUILD_FOLDER) + "' folder and run 'library-manager.exe'")
    return True

if __name__ == '__main__':
    build()
