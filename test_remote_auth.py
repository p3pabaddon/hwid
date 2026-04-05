from license_manager import LicenseManager
import time
import os

# Ensure server is running before this
lm = LicenseManager(".")

print("Testing Remote Auth...")
# 1. Login as Admin
if lm.verify_admin("xR00t_4dm", "123456"):
    print("Admin Login OK")
    
    # 2. Generate key
    key = lm.generate_key(duration_days=30, is_pro=True)
    print(f"Generated Key: {key}")
    
    if key and "ERROR" not in key:
        # 3. Validate key
        ok, msg = lm.validate_key(key)
        print(f"Validation (New): {ok}, {msg}")
        
        # 4. Consume key
        if lm.consume_key(key):
            print("Key Consumed OK")
            
            # 5. Validate again (should be bound to HWID)
            ok, msg = lm.validate_key(key)
            print(f"Validation (Used): {ok}, {msg}")
        else:
            print("Failed to consume key")
    else:
        print("Failed to generate key")
else:
    print("Admin Login Failed")
