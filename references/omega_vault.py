# SPDX-License-Identifier: MIT OR Apache-2.0
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class OmegaVault:
    """Handles AES-256-GCM encryption for project wisdom."""
    def __init__(self, key_path="system_scripts/master.key"):
        if not os.path.exists(key_path):
            self.key = AESGCM.generate_key(bit_length=256)
            with open(key_path, "wb") as f: f.write(self.key)
        else:
            with open(key_path, "rb") as f: self.key = f.read()
        self.cipher = AESGCM(self.key)

    def secure_store(self, plaintext: str) -> bytes:
        nonce = os.urandom(12)
        return nonce + self.cipher.encrypt(nonce, plaintext.encode(), None)

    def secure_retrieve(self, ciphertext: bytes) -> str:
        return self.cipher.decrypt(ciphertext[:12], ciphertext[12:], None).decode()


class OmegaVault:
    def __init__(self, master_key_path="system_scripts/master.key"):
        # Generate or load the 256-bit key
        if not os.path.exists(master_key_path):
            self.key = AESGCM.generate_key(bit_length=256)
            with open(master_key_path, "wb") as f: f.write(self.key)
        else:
            with open(master_key_path, "rb") as f: self.key = f.read()
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, data: str) -> bytes:
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, data.encode(), None)
        return nonce + ciphertext

    def decrypt(self, encrypted_data: bytes) -> str:
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None).decode()
