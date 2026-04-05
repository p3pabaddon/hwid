from flask import Flask, request, jsonify
import hashlib
import sqlite3
import datetime
import secrets
import base64
import os


app = Flask(__name__)
DB_NAME = "licensing.db"

# Admin credentials matching license_manager.py
# user: r00t_4dm (eFIwMHRfNGRt)
# pass: solutions2024 (hash check matched)
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS keys 
                 (key TEXT PRIMARY KEY, hwid TEXT, expiry TEXT, status TEXT, is_pro INTEGER, used INTEGER)''')
    conn.commit()
    conn.close()

def check_auth(auth_header):
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    try:
        encoded = auth_header.split(" ")[1]
        decoded = base64.b64decode(encoded).decode()
        u, p = decoded.split(":")
        return u == ADMIN_USER and p == ADMIN_PASS
    except:
        return False

@app.route('/v1/consume', methods=['POST'])
def consume_key():
    # State is managed by validate/db, but we provide this for client compatibility
    return jsonify({"success": True, "message": "Key consumed."})

@app.route('/v1/validate', methods=['POST'])
def validate_key():
    data = request.json
    key_str = data.get("key")
    hwid = data.get("hwid")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT hwid, expiry, status, is_pro FROM keys WHERE key=?", (key_str,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"success": False, "message": "Geçersiz anahtar."}), 200
        
    db_hwid, db_expiry, db_status, is_pro = row
    
    if db_hwid and db_hwid != hwid:
        conn.close()
        return jsonify({"success": False, "message": "Bu anahtar başka bir cihazda kullanılıyor."}), 200
        
    # Bind on validate if not bound
    if not db_hwid:
        c.execute("UPDATE keys SET hwid=?, used=1 WHERE key=?", (hwid, key_str))
        conn.commit()
        
    expiry_dt = datetime.datetime.fromisoformat(db_expiry)
    if datetime.datetime.now() > expiry_dt:
        return jsonify({"success": False, "message": "Anahtar süresi dolmuş."}), 200

    conn.close()
    return jsonify({"success": True, "message": "Doğrulandı.", "info": {"is_pro": bool(is_pro), "expiry": db_expiry}})

@app.route('/v1/admin/generate', methods=['POST'])
def generate_key():
    if not check_auth(request.headers.get("Authorization")):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    days = data.get("duration_days", 30)
    is_pro = 1 if data.get("is_pro") else 0
    
    new_key = f"{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
    
    # Handle lifetime keys (0 or -1) as 10 years
    if days <= 0:
        expiry_days = 3650
    else:
        expiry_days = days
        
    expiry = (datetime.datetime.now() + datetime.timedelta(days=expiry_days)).isoformat()
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO keys (key, hwid, expiry, status, is_pro, used) VALUES (?, ?, ?, ?, ?, ?)", 
              (new_key, None, expiry, "active", is_pro, 0))
    conn.commit()
    conn.close()
    
    return jsonify({"key": new_key})

@app.route('/v1/admin/add_key', methods=['POST'])
def add_key():
    if not check_auth(request.headers.get("Authorization")):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    key_str = data.get("key")
    days = data.get("duration_days", 30)
    is_pro = 1 if data.get("is_pro") else 0
    
    if not key_str:
        return jsonify({"error": "Key required"}), 400
        
    # Handle lifetime keys (0 or -1) as 10 years
    expiry_days = days if days > 0 else 3650
    expiry = (datetime.datetime.now() + datetime.timedelta(days=expiry_days)).isoformat()
    
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO keys (key, hwid, expiry, status, is_pro, used) VALUES (?, ?, ?, ?, ?, ?)", 
                  (key_str.upper(), None, expiry, "active", is_pro, 0))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "key": key_str.upper()}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Key already exists"}), 400

@app.route('/v1/admin/keys', methods=['GET'])
def get_keys():
    if not check_auth(request.headers.get("Authorization")):
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT key, hwid, expiry, status, is_pro, used FROM keys")
    rows = c.fetchall()
    conn.close()
    
    keys = []
    for r in rows:
        keys.append({"key": r[0], "hwid": r[1], "expiry": r[2], "status": r[3], "is_pro": bool(r[4]), "used": bool(r[5])})
    return jsonify(keys)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
