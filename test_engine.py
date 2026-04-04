import sys
import os

# Add the app directory to sys.path
app_dir = r"c:\Users\asrin\Downloads\antigravity-god-mode-main\antigravity-god-mode-main\Monotone-HWID-Spoofer"
sys.path.append(app_dir)

from app import SpoofEngine

def test_engine_methods():
    engine = SpoofEngine(app_dir)
    
    # Test methods presence
    assert hasattr(engine, "raid0_simulation")
    assert hasattr(engine, "optimize_system")
    
    print("Methods raid0_simulation and optimize_system are present.")
    
    # Optional: Test if they run without crashing (simulated)
    # Note: These call powershell/reg, so they might fail in restricted env
    # but we just want to see if the interface is correct.
    print("Engine Interface Verification Successful.")

if __name__ == "__main__":
    test_engine_methods()
