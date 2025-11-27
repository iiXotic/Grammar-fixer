import PyInstaller.__main__
import shutil
import os

def build():
    print("Building GrammarFixer...")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # Run PyInstaller
    PyInstaller.__main__.run([
        'GrammarFixer.spec',
        '--noconfirm'
    ])
    
    print("Build complete. Executable is in dist/GrammarFixer/")

if __name__ == "__main__":
    build()
