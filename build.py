import subprocess
import sys
import os
import shutil

def build():
    print("=== Solutions-Spoofer Build Script ===")
    
    # Ensure we are in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    print("Checking dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "customtkinter", "pillow", "requests", "flask"], check=True)
    
    # 2. Cleanup old builds
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            
    # 3. Build command
    # --onefile: single exe
    # --noconsole: hide console window
    # --uac-admin: request admin privileges on start
    # --name: output name
    # --icon: if available (currently None)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--uac-admin",
        "--name", "Solutions-Spoofer",
        "--add-data", "engine.py;.",
        "--add-data", "license_manager.py;.",
        "app.py"
    ]
    
    print(f"Running build command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    print("\n[SUCCESS] EXE created in 'dist' folder.")
    print("Note: In production, consider using pyarmor for obfuscation.")

if __name__ == "__main__":
    try:
        build()
    except Exception as e:
        print(f"\n[ERROR] Build interrupted: {e}")
    finally:
        input("\nKapatmak için Enter'a basın...")
