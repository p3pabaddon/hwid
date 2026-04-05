import requests
import json
import sys

import base64

# Konfigürasyon
SERVER_URL = "http://localhost:5001"
ADMIN_USER = "r00t_adm"
ADMIN_PASS = "123456"

def get_auth_header():
    """Create Basic Auth header."""
    auth_str = f"{ADMIN_USER}:{ADMIN_PASS}"
    encoded = base64.b64encode(auth_str.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}

def generate_keys(count=1, days=30):
    """Generate new license keys."""
    headers = get_auth_header()
    keys = []
    print(f"\n--- {count} Adet {days} Günlük Anahtar Üretiliyor ---\n")
    
    for i in range(count):
        try:
            response = requests.post(f"{SERVER_URL}/v1/admin/generate", 
                                     headers=headers, 
                                     json={"duration_days": days}, 
                                     timeout=5)
            if response.status_code == 200:
                key = response.json().get("key")
                keys.append(key)
                print(f"[{i+1}] Üretildi: {key}")
            elif response.status_code == 401:
                print(f"Hata: Yetkisiz erişim! Kullanıcı adı veya şifre yanlış.")
                return
            else:
                print(f"[{i+1}] Hata: {response.status_code}")
        except Exception as e:
            print(f"[{i+1}] Hata: {e}")
            
    print("\n--- İşlem Tamamlandı ---")

def list_keys():
    """List all license keys and their status."""
    headers = get_auth_header()
    try:
        response = requests.get(f"{SERVER_URL}/v1/admin/keys", headers=headers, timeout=5)
        if response.status_code == 200:
            keys = response.json()
            print("\n" + "="*80)
            print(f"{'ANAHTAR':<25} | {'GÜN':<5} | {'DURUM':<15} | {'BAĞLI HWID'}")
            print("-" * 80)
            for k in keys:
                status = "Kullanıldı" if k['hwid'] else "Kullanılmadı"
                hwid = k['hwid'] if k['hwid'] else "---"
                print(f"{k['key']:<25} | {k['days']:<5} | {status:<15} | {hwid}")
            print("="*80 + "\n")
        else:
            print(f"Hata: Listeleme başarısız (Status: {response.status_code})")
    except Exception as e:
        print(f"Hata: {e}")

def main():
    print("Solutions Admin Kontrol Paneli")
    print("1. Yeni Anahtar Üret")
    print("2. Tüm Anahtarları Listele")
    print("3. Çıkış")
    
    choice = input("\nSeçiminiz: ")
    
    if choice == '1':
        count = int(input("Kaç adet anahtar üretilsin? (Örn: 5): "))
        days = int(input("Kaç günlük olsun? (Örn: 30): "))
        generate_keys(count, days)
    elif choice == '2':
        list_keys()
    elif choice == '3':
        sys.exit()
    else:
        print("Geçersiz seçim.")

if __name__ == "__main__":
    while True:
        main()
        input("\nDevam etmek için Enter'a basın...")
