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
            return "ERROR: Not authenticated"
            
        try:
            print(f"DEBUG: Sending request to {SERVER_URL}/v1/admin/add_key")
            headers = {"Authorization": f"Basic {self.admin_auth}"}
            payload = {
                "key": custom_key, 
                "duration_days": duration_days, 
                "is_pro": is_pro
            }
            # Use /v1/admin/add_key if custom_key is provided, else /v1/admin/generate
            endpoint = "/v1/admin/add_key" if custom_key else "/v1/admin/generate"
            response = requests.post(f"{SERVER_URL}{endpoint}", json=payload, headers=headers, timeout=5)
            
            if response.status_code == 200:
                return response.json().get("key")
        except:
            pass
        return "ERROR"

    def get_all_keys(self):
        """Admin: Get all keys from Server."""
        if not self.admin_auth: return []
        try:
            resp = requests.get(f"{SERVER_URL}/v1/admin/keys",
                                headers={"Authorization": f"Basic {self.admin_auth}"},
                                timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except:
            pass
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
        ADMIN_USER_ENC = "YWRtaW4=" # admin
        ADMIN_PASS_HASH = "240be518fabd2724ddb6f0403bc3d59d47348c9bc88a961d55656013ef23018c" # admin123
        
        user_match_val = base64.b64encode(username.encode()).decode()
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if user_match_val == ADMIN_USER_ENC and pass_hash == ADMIN_PASS_HASH:
            auth_str = f"{username}:{password}"
            self.admin_auth = base64.b64encode(auth_str.encode()).decode()
            return True
        return False
