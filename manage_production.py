import requests
import json

# PRODUCTION SERVER SETTINGS
SERVER_URL = "https://hwid-sl1a.onrender.com"
ADMIN_USER = "r00t_4dm"
ADMIN_PASS = "solutions2024"

def add_license(key, duration_days=30):
    """Adds a new license key to the production server."""
    url = f"{SERVER_URL}/v1/admin/add_key"
    payload = {
        "key": key,
        "duration_days": duration_days
    }
    try:
        response = requests.post(url, json=payload, auth=(ADMIN_USER, ADMIN_PASS))
        if response.status_code == 201:
            print(f"[SUCCESS] Key '{key}' added for {duration_days} days.")
        else:
            print(f"[ERROR] {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[CONNECTION ERROR] {e}")

def generate_random_key(length=4, segments=3):
    """Generates a random key like XXXX-XXXX-XXXX."""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    return "-".join("".join(random.choice(chars) for _ in range(length)) for _ in range(segments))

if __name__ == "__main__":
    print(f"--- Production License Manager ({SERVER_URL}) ---")
    print("Tip: Leave blank to generate a random key (XXXX-XXXX-XXXX)")
    
    new_key = input("Enter new license key: ").strip().upper()
    if not new_key:
        new_key = generate_random_key()
        print(f"Generated random key: {new_key}")
        
    days = input("Duration (days) [default 30]: ") or 30
    add_license(new_key, int(days))
