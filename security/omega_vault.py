"""
OMEGA-CODE Zero-Trust Security Layer
====================================
At-Rest Encryption using AES-256-GCM

Features:
- AES-256-GCM encryption for project wisdom
- Secure store and retrieve operations
- Master key management
"""

import os
from pathlib import Path
from typing import Optional, Union
from dataclasses import dataclass
from datetime import datetime
import secrets as stdlib_secrets

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

@dataclass
class VaultStats:
    """Statistics about the vault."""
    key_exists: bool
    key_size: int
    last_rotated: Optional[str]
    entries_encrypted: int


class OmegaVault:
    """
    Handles AES-256-GCM encryption for project wisdom.
    
    Security features:
    - AES-256-GCM authenticated encryption
    - Random 96-bit nonce per encryption
    - Keys never stored with encrypted data
    - Secure key generation using CSPRNG
    """
    
    KEY_SIZE = 32  # 256 bits
    NONCE_SIZE = 12  # 96 bits (GCM standard)
    
    def __init__(self, key_path: str = None, project: str = None):
        self.project = project or os.getenv("PROJECT_NAME", "default")
        self.key_dir = Path(f"projects/{self.project}/state")
        self.key_path = Path(key_path) if key_path else self.key_dir / "master.key"
        
        self.key_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.key_path.exists():
            self._generate_key()
        
        self._load_key()
        self.aesgcm = AESGCM(self.key) if HAS_CRYPTO else None
    
    def _generate_key(self):
        """Generate a new 256-bit AES key using CSPRNG."""
        if not HAS_CRYPTO:
            raise ImportError("cryptography library required. Install: pip install cryptography")
        
        print("[VAULT] Generating new AES-256 key...")
        self.key = AESGCM.generate_key(bit_length=256)
        
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.key_path, "wb") as f:
            f.write(self.key)
        
        self.key_path.chmod(0o600)
        print(f"[VAULT] Key stored at: {self.key_path}")
    
    def _load_key(self):
        """Load the master key from disk."""
        if not self.key_path.exists():
            raise FileNotFoundError(f"Key not found at {self.key_path}")
        
        with open(self.key_path, "rb") as f:
            self.key = f.read()
        
        if len(self.key) != self.KEY_SIZE:
            raise ValueError(f"Invalid key size: {len(self.key)} (expected {self.KEY_SIZE})")
    
    def secure_store(self, plaintext: str) -> bytes:
        """
        Encrypt plaintext using AES-256-GCM.
        Returns: nonce (12 bytes) + ciphertext + auth_tag (16 bytes)
        """
        if not self.aesgcm:
            raise ImportError("cryptography library required")
        
        nonce = stdlib_secrets.token_bytes(self.NONCE_SIZE)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        
        return nonce + ciphertext
    
    def secure_retrieve(self, encrypted_data: bytes) -> str:
        """
        Decrypt AES-256-GCM encrypted data.
        Input: nonce (12 bytes) + ciphertext + auth_tag (16 bytes)
        """
        if not self.aesgcm:
            raise ImportError("cryptography library required")
        
        nonce = encrypted_data[:self.NONCE_SIZE]
        ciphertext = encrypted_data[self.NONCE_SIZE:]
        
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')
    
    def encrypt_file(self, plaintext_path: Union[str, Path], 
                     encrypted_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Encrypt a file and save as .enc extension.
        """
        plaintext_path = Path(plaintext_path)
        
        if encrypted_path is None:
            encrypted_path = plaintext_path.with_suffix(plaintext_path.suffix + '.enc')
        
        with open(plaintext_path, 'r', encoding='utf-8') as f:
            plaintext = f.read()
        
        encrypted = self.secure_store(plaintext)
        
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted)
        
        return Path(encrypted_path)
    
    def decrypt_file(self, encrypted_path: Union[str, Path],
                    plaintext_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Decrypt an encrypted file.
        """
        encrypted_path = Path(encrypted_path)
        
        if plaintext_path is None:
            plaintext_path = encrypted_path.with_suffix('')
            if str(plaintext_path).endswith('.enc'):
                plaintext_path = Path(str(plaintext_path)[:-4])
        
        with open(encrypted_path, 'rb') as f:
            encrypted = f.read()
        
        plaintext = self.secure_retrieve(encrypted)
        
        with open(plaintext_path, 'w', encoding='utf-8') as f:
            f.write(plaintext)
        
        return Path(plaintext_path)
    
    def encrypt_to_file(self, plaintext: str, output_path: Union[str, Path]):
        """Encrypt string and write to file."""
        encrypted = self.secure_store(plaintext)
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    
    def decrypt_from_file(self, input_path: Union[str, Path]) -> str:
        """Read encrypted file and decrypt."""
        with open(input_path, 'rb') as f:
            encrypted = f.read()
        return self.secure_retrieve(encrypted)
    
    def rotate_key(self) -> bytes:
        """
        Rotate to a new key.
        Returns old key for re-encryption.
        """
        old_key = self.key
        
        self._generate_key()
        self._load_key()
        self.aesgcm = AESGCM(self.key)
        
        return old_key
    
    def get_stats(self) -> VaultStats:
        """Get vault statistics."""
        key_exists = self.key_path.exists()
        key_size = len(self.key) if key_exists else 0
        
        last_rotated = None
        if key_exists:
            mtime = self.key_path.stat().st_mtime
            last_rotated = datetime.fromtimestamp(mtime).isoformat()
        
        return VaultStats(
            key_exists=key_exists,
            key_size=key_size,
            last_rotated=last_rotated,
            entries_encrypted=0
        )
    
    def verify_key(self, test_plaintext: str = "OMEGA-VAULT-TEST") -> bool:
        """Verify the key can encrypt and decrypt correctly."""
        try:
            encrypted = self.secure_store(test_plaintext)
            decrypted = self.secure_retrieve(encrypted)
            return decrypted == test_plaintext
        except Exception as e:
            print(f"[VAULT] Verification failed: {e}")
            return False


def create_vault(project: str = None) -> OmegaVault:
    """Create and initialize a vault for a project."""
    return OmegaVault(project=project)


def encrypt_wisdom(project: str, wisdom: str, filename: str = "wisdom.enc") -> Path:
    """Encrypt and store project wisdom."""
    vault = OmegaVault(project=project)
    output_path = Path(f"projects/{project}/state/{filename}")
    vault.encrypt_to_file(wisdom, output_path)
    return output_path


def decrypt_wisdom(project: str, filename: str = "wisdom.enc") -> str:
    """Decrypt project wisdom."""
    vault = OmegaVault(project=project)
    input_path = Path(f"projects/{project}/state/{filename}")
    return vault.decrypt_from_file(input_path)


if __name__ == "__main__":
    import sys
    
    project = sys.argv[1] if len(sys.argv) > 1 else os.getenv("PROJECT_NAME", "default")
    
    print("=" * 60)
    print("OMEGA-CODE VAULT: AES-256-GCM Encryption")
    print("=" * 60)
    
    if not HAS_CRYPTO:
        print("[ERROR] cryptography library not installed")
        print("Install with: pip install cryptography")
        sys.exit(1)
    
    vault = OmegaVault(project=project)
    
    print(f"\nProject: {project}")
    print(f"Key Path: {vault.key_path}")
    
    stats = vault.get_stats()
    print(f"Key Exists: {stats.key_exists}")
    print(f"Key Size: {stats.key_size} bytes")
    
    if vault.verify_key():
        print("\n[OK] Key verification passed")
    else:
        print("\n[ERROR] Key verification failed")
        sys.exit(1)
    
    print("\n[TEST] Encrypt/Decrypt test...")
    test_data = "Secret OMEGA-CODE wisdom"
    encrypted = vault.secure_store(test_data)
    decrypted = vault.secure_retrieve(encrypted)
    
    if decrypted == test_data:
        print(f"  Encrypted: {len(encrypted)} bytes")
        print(f"  Decrypted: {decrypted}")
        print("[OK] Encryption test passed")
    else:
        print("[ERROR] Encryption test failed")
        sys.exit(1)
    
    print("=" * 60)

SecureVault = OmegaVault
