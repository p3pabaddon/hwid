import os
import json
import base64
import random
import time
import uuid
import subprocess
import hashlib
import requests

SERVER_URL = "https://hwid-sl1a.onrender.com"

class LicenseManager:
    """Manages timed license keys via Remote Server API."""

    def __init__(self, base_path):
        self.base_path = base_path
        self.admin_auth = None # Will be set on login

    def get_hwid(self):
        try:
            cmd = "powershell -Command \"(Get-CimInstance Win32_ComputerSystemProduct).UUID\""
            out = subprocess.check_output(cmd, shell=True).decode().strip()
            if out: return out
            return str(uuid.getnode())
        except:
            return str(uuid.getnode())

    def validate_key(self, key):
        """Check if key is valid via Server API."""
        try:
            hwid = self.get_hwid()
            resp = requests.post(f"{SERVER_URL}/v1/validate", 
                                 json={"key": key, "hwid": hwid},
                                 timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return data["success"], data["message"]
            return False, f"Sunucu hatası: {resp.status_code}"
        except Exception as e:
            return False, f"Bağlantı hatası: {str(e)}"

    def consume_key(self, key):
        """Bind key to HWID via Server API."""
        try:
            hwid = self.get_hwid()
            resp = requests.post(f"{SERVER_URL}/v1/consume", 
                                 json={"key": key, "hwid": hwid},
                                 timeout=5)
            return resp.status_code == 200 and resp.json().get("success", False)
        except:
            return False

    def consume_spoof(self, key):
        """Decrement uses count via Server API (if applicable)."""
        # In remote mode, we just validate again to see if still active
        # Or we could add a specific consume_spoof endpoint if needed.
        # For now, validation is enough as server handles state.
        return True

    def get_key_info(self, key):
        """Get key metadata from Server."""
        try:
            hwid = self.get_hwid()
            resp = requests.post(f"{SERVER_URL}/v1/validate", 
                                 json={"key": key, "hwid": hwid},
                                 timeout=5)
            if resp.status_code == 200:
                return resp.json().get("info")
        except:
            pass
        return None

    def generate_key(self, duration_days=30, is_pro=False, custom_key=None):
        if not self.admin_auth:
            return "ERROR: AUTH REQUIRED"
            
        try:
            # We use requests built-in auth for better header handling
            u, p = base64.b64decode(self.admin_auth).decode().split(":")
            auth = (u, p)
            
            payload = {
                "key": custom_key, 
                "duration_days": duration_days, 
                "is_pro": is_pro
            }
            # Use /v1/admin/add_key if custom_key is provided, else /v1/admin/generate
            endpoint = "/v1/admin/add_key" if custom_key else "/v1/admin/generate"
            response = requests.post(f"{SERVER_URL}{endpoint}", json=payload, auth=auth, timeout=5)
            
            if response.status_code in [200, 201]:
                data = response.json()
                # Server might return key directly or inside success
                if data.get("success") or "key" in data:
                    return data.get("key")
                return f"ERROR: {data.get('message', data.get('error', 'Unknown server error'))}"
            return f"ERROR: HTTP {response.status_code}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_all_keys(self):
        """Admin: Get all keys from Server."""
        if not self.admin_auth: return []
        try:
            u, p = base64.b64decode(self.admin_auth).decode().split(":")
            resp = requests.get(f"{SERVER_URL}/v1/admin/keys",
                                auth=(u, p),
                                timeout=5)
            if resp.status_code == 200:
                return resp.json()
            print(f"DEBUG: get_all_keys failed with {resp.status_code}")
        except Exception as e:
            print(f"DEBUG: get_all_keys exception: {e}")
        return []

    def get_stats(self):
        """Admin: Get stats from Server."""
        keys = self.get_all_keys()
        total = len(keys)
        used = sum(1 for k in keys if k["used"])
        return total, used, total - used

    def verify_admin(self, username, password):
        """Verify admin locally + cache auth for API."""
        # We verify locally to allow server-less admin panel if needed,
        # but the API will also verify on every request.
        # User: Sol_Admin_X -> U29sX0FkbWluX1g=
        # Pass: Solutions#2024!Root -> 1e9bdae3491aabf0e6b84b00071f8acf47a8461800998f81e37f19d777a6b59f
        ADMIN_USER_ENC = "U29sX0FkbWluX1g="
        ADMIN_PASS_HASH = "1e9bdae3491aabf0e6b84b00071f8acf47a8461800998f81e37f19d777a6b59f"
        
        user_match_val = base64.b64encode(username.encode()).decode()
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if user_match_val == ADMIN_USER_ENC and pass_hash == ADMIN_PASS_HASH:
            auth_str = f"{username}:{password}"
            self.admin_auth = base64.b64encode(auth_str.encode()).decode()
            return True
        return False
