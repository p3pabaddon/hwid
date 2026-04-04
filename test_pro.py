import sys
import os
import json
import base64
import time

# Add the app directory to sys.path
app_dir = r"c:\Users\asrin\Downloads\antigravity-god-mode-main\antigravity-god-mode-main\Monotone-HWID-Spoofer"
sys.path.append(app_dir)

from app import LicenseManager

def test_license_manager():
    lm = LicenseManager(app_dir)
    
    # Generate a Standard Key
    std_key = lm.generate_key(duration_days=1, pro=False)
    print(f"Generated Standard Key: {std_key}")
    
    # Generate a Pro Key
    pro_key = lm.generate_key(duration_days=0, pro=True)
    print(f"Generated Pro Key: {pro_key}")
    
    # Verify Metadata
    std_info = lm.get_key_info(std_key)
    pro_info = lm.get_key_info(pro_key)
    
    print(f"Standard Info - is_pro: {std_info.get('is_pro')}")
    print(f"Pro Info - is_pro: {pro_info.get('is_pro')}")
    
    assert std_info.get('is_pro') == False
    assert pro_info.get('is_pro') == True
    print("Verification Successful: LicenseManager handles PRO flag correctly.")

if __name__ == "__main__":
    test_license_manager()
