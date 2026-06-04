# SPDX-License-Identifier: MIT OR Apache-2.0
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import sqlite3

def rotate_omega_keys(db_path, key_path):
    """Generates a new key and re-encrypts all DB entries."""
    if not os.path.exists(key_path): return
    
    with open(key_path, "rb") as f: old_key = f.read()
    new_key = AESGCM.generate_key(bit_length=256)
    
    old_cipher, new_cipher = AESGCM(old_key), AESGCM(new_key)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Re-encrypt every 'logs' entry in the state table
    for row_id, data in cursor.execute("SELECT id, logs FROM state"):
        try:
            # Decrypt with old, encrypt with new
            decrypted = old_cipher.decrypt(data[:12], data[12:], None)
            nonce = os.urandom(12)
            encrypted = nonce + new_cipher.encrypt(nonce, decrypted, None)
            cursor.execute("UPDATE state SET logs = ? WHERE id = ?", (encrypted, row_id))
        except Exception: continue

    conn.commit()
    with open(key_path, "wb") as f: f.write(new_key)
    print(f"✅ Key rotated and data re-encrypted at {db_path}")
