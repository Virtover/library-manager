"""
Build script to create standalone executables for Library Manager and Books Viewer
Run: python build.py
"""
import subprocess
import shutil
import os
import sys
from pathlib import Path

BUILD_FOLDER_MANAGER = Path("MSF Library Manager")
BUILD_FOLDER_VIEWER = Path("MSF Library Manager/books-viewer")

def build_manager():
    """Build the Library Manager application"""
    print("\n=== Building Library Manager ===")
    
    # Create build folder
    BUILD_FOLDER_MANAGER.mkdir(exist_ok=True)
    
    # Get absolute icon path
    icon_path = Path("icon/msf-favicon.ico").absolute()
    
    # Run PyInstaller for manager
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'library-manager',
        '--distpath', str(BUILD_FOLDER_MANAGER),
        '--workpath', 'build/manager',
        '--specpath', 'build',
        '--hidden-import=pandas',
        '--hidden-import=sqlite3',
        f'--icon={icon_path}',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("[OK] Manager executable created")
    except subprocess.CalledProcessError as e:
        print(f"[FAILED] Manager build failed: {e}")
        return False
    
    return True

def build_viewer():
    """Build the Books Viewer application"""
    print("\n=== Building Books Viewer ===")
    
    # Create viewer build folder
    BUILD_FOLDER_VIEWER.mkdir(parents=True, exist_ok=True)
    
    # Get absolute icon path
    icon_path = Path("icon/msf-favicon.ico").absolute()
    
    # Run PyInstaller for viewer
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'books-viewer',
        '--distpath', str(BUILD_FOLDER_VIEWER),
        '--workpath', 'build/viewer',
        '--specpath', 'build',
        '--hidden-import=pandas',
        f'--icon={icon_path}',
        'books-viewer/viewer.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("[OK] Viewer executable created")
    except subprocess.CalledProcessError as e:
        print(f"[FAILED] Viewer build failed: {e}")
        return False
    
    return True

def build():
    print("Building Library Manager and Books Viewer...")
    
    # Build manager
    if not build_manager():
        return False
    
    # Build viewer
    if not build_viewer():
        return False
    
    # Copy icon folder to both builds
    for target_folder in [BUILD_FOLDER_MANAGER, BUILD_FOLDER_VIEWER]:
        icon_src = Path("icon")
        icon_dst = target_folder / "icon"
        if icon_src.exists():
            if icon_dst.exists():
                shutil.rmtree(icon_dst)
            shutil.copytree(icon_src, icon_dst)
    print("[OK] Copied icon folders")
    
    # Create empty books.tsv in viewer folder
    tsv_path = BUILD_FOLDER_VIEWER / "books.tsv"
    if not tsv_path.exists():
        with open(tsv_path, 'w') as f:
            f.write("ISBN\tTitle\tAuthor\tPublisher\tYear\tSignature\tDescription\tKeywords\n")
        print(f"[OK] Created {tsv_path}")
    
    # Cleanup build artifacts
    if Path('build').exists():
        shutil.rmtree('build')
    
    print("\n[OK] Build complete!")
    print(f"  Manager: {BUILD_FOLDER_MANAGER / 'library-manager.exe'}")
    print(f"  Viewer:  {BUILD_FOLDER_VIEWER / 'books-viewer.exe'}")
    print(f"\nTo run:")
    print(f"  - Manager: Open '{BUILD_FOLDER_MANAGER}' and run 'library-manager.exe'")
    print(f"  - Viewer:  Open '{BUILD_FOLDER_VIEWER}' and run 'books-viewer.exe'")
    return True

if __name__ == '__main__':
    build()
