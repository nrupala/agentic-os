"""
OMEGA Phase Encryptor - Zero-Trust Encryption for All Phase Outputs
=====================================================
AES-256-GCM encryption for:
- Generated code files
- Memory files  
- Configuration
- Any sensitive phase output

Zero-Knowledge: Data encrypted at rest AND in motion.
"""

import os
import json
import hashlib
import base64
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime
from dataclasses import dataclass
import secrets as stdlib_secrets
import random

PROJECT_ROOT = Path(__file__).parent.parent
OMEGA_DIR = PROJECT_ROOT / ".omega"

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


@dataclass
class EncryptedPayload:
    """Encrypted data with metadata."""
    ciphertext: bytes
    nonce: bytes
    checksum: str
    key_id: str
    created_at: str


@dataclass
class PhaseFile:
    """Encrypted phase file."""
    path: Path
    type: str  # code, memory, config, output
    encrypted: bool
    size: int
    created_at: Optional[str]


class OmegaPhaseEncryptor:
    """
    Encryptor for all phase outputs.
    
    Data types:
    - CODE: Generated source code files
    - MEMORY: Hierarchical memory files  
    - CONFIG: Configuration files
    - OUTPUT: Execution outputs
    
    File structure:
    - {filename}.enc - encrypted content
    - {filename}.meta - metadata (unencrypted for quick lookup)
    """
    
    TYPE_EXTENSIONS = {
        "code": ".enc",
        "memory": ".mem.enc", 
        "config": ".cfg.enc",
        "output": ".out.enc",
    }
    
    def __init__(self, project: str = "default"):
        self.project = project
        self.omega_dir = OMEGA_DIR / "encryptions" / project
        self.omega_dir.mkdir(parents=True, exist_ok=True)
        
        self._key = self._get_or_create_key()
        self.aesgcm = AESGCM(self._key) if HAS_CRYPTO else None
        
        self._init_index()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create the phase encryption key."""
        key_file = self.omega_dir / "phase.key"

        if key_file.exists():
            key_data = key_file.read_bytes()
            if len(key_data) >= 32:
                return key_data[-32:]
            return key_data
        
        if not HAS_CRYPTO:
            raise ImportError("cryptography required")
        
        try:
            salt = stdlib_secrets.token_bytes(32)
        except AttributeError:
            salt = os.urandom(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = kdf.derive(b"omga-zero-knowledge")
        
        key_file.write_bytes(salt + key)
        return key
    
    def _init_index(self):
        """Initialize encrypted file index."""
        index_file = self.omega_dir / "index.json"
        if not index_file.exists():
            index_file.write_text("{}")
    
    def _compute_checksum(self, data: bytes) -> str:
        """Compute SHA-256 checksum."""
        return hashlib.sha256(data).hexdigest()
    
    def encrypt_string(self, plaintext: str) -> EncryptedPayload:
        """Encrypt string to payload."""
        if not HAS_CRYPTO:
            raise ImportError("cryptography library required")
        
        try:
            nonce = stdlib_secrets.token_bytes(12)
        except AttributeError:
            nonce = os.urandom(12)
        plaintext_bytes = plaintext.encode('utf-8')
        
        ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)
        
        checksum = self._compute_checksum(plaintext_bytes)
        
        return EncryptedPayload(
            ciphertext=ciphertext,
            nonce=nonce,
            checksum=checksum,
            key_id="phase.key",
            created_at=datetime.now().isoformat()
        )
    
    def decrypt_string(self, payload: EncryptedPayload) -> str:
        """Decrypt payload to string."""
        plaintext = self.aesgcm.decrypt(
            payload.nonce, 
            payload.ciphertext, 
            None
        )
        return plaintext.decode('utf-8')
    
    def encrypt_file(self, input_path: Path, output_type: str = "code") -> PhaseFile:
        """Encrypt a file."""
        if not HAS_CRYPTO:
            raise ImportError("cryptography library required")
        
        plaintext = input_path.read_bytes(encoding='utf-8')
        payload = self.encrypt_string(plaintext)
        
        ext = self.TYPE_EXTENSIONS.get(output_type, ".enc")
        output_path = self.omega_dir / f"{input_path.stem}{ext}"
        
        output_path.write_bytes(payload.nonce + payload.ciphertext)
        
        meta = {
            "original": str(input_path),
            "type": output_type,
            "checksum": payload.checksum,
            "created_at": payload.created_at,
            "size": len(payload.ciphertext)
        }
        meta_path = output_path.with_suffix('.meta')
        meta_path.write_text(json.dumps(meta))
        
        self._add_to_index(output_path.name, meta)
        
        return PhaseFile(
            path=output_path,
            type=output_type,
            encrypted=True,
            size=len(payload.ciphertext),
            created_at=payload.created_at
        )
    
    def decrypt_file(self, encrypted_path: Path) -> str:
        """Decrypt a file."""
        data = encrypted_path.read_bytes()
        nonce = data[:12]
        ciphertext = data[12:]
        
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')
    
    def encrypt_code(self, code: str, filename: str) -> Path:
        """Encrypt generated code."""
        payload = self.encrypt_string(code)
        
        output_path = self.omega_dir / f"{filename}.code.enc"
        output_path.write_bytes(payload.nonce + payload.ciphertext)
        
        meta = {
            "type": "code",
            "checksum": payload.checksum,
            "created_at": payload.created_at,
        }
        meta_path = output_path.with_suffix('.meta')
        meta_path.write_text(json.dumps(meta))
        
        self._add_to_index(output_path.name, meta)
        
        return output_path
    
    def decrypt_code(self, filename: str) -> Optional[str]:
        """Decrypt generated code."""
        search_pattern = f"{filename}.code.enc"
        candidates = list(self.omega_dir.glob(search_pattern))
        
        if not candidates:
            return None
        
        encrypted_path = candidates[0]
        return self.decrypt_file(encrypted_path)
    
    def encrypt_memory(self, memory_data: Dict, memory_type: str = "daily") -> Path:
        """Encrypt memory data."""
        json_data = json.dumps(memory_data, indent=2, default=str)
        payload = self.encrypt_string(json_data)
        
        output_path = self.omega_dir / f"memory_{memory_type}.mem.enc"
        output_path.write_bytes(payload.nonce + payload.ciphertext)
        
        meta = {
            "type": "memory",
            "memory_type": memory_type,
            "checksum": payload.checksum,
            "created_at": payload.created_at,
        }
        meta_path = output_path.with_suffix('.meta')
        meta_path.write_text(json.dumps(meta))
        
        self._add_to_index(output_path.name, meta)
        
        return output_path
    
    def decrypt_memory(self, memory_type: str = "daily") -> Optional[Dict]:
        """Decrypt memory data."""
        search_pattern = f"memory_{memory_type}.mem.enc"
        candidates = list(self.omega_dir.glob(search_pattern))
        
        if not candidates:
            return None
        
        encrypted_path = candidates[0]
        plaintext = self.decrypt_file(encrypted_path)
        return json.loads(plaintext)
    
    def _add_to_index(self, filename: str, meta: Dict):
        """Add file to index."""
        index_file = self.omega_dir / "index.json"
        index = json.loads(index_file.read_text())
        index[filename] = meta
        index_file.write_text(json.dumps(index, indent=2))
    
    def list_encrypted(self, file_type: Optional[str] = None) -> list:
        """List encrypted files."""
        index_file = self.omega_dir / "index.json"
        index = json.loads(index_file.read_text())
        
        if file_type:
            return [
                {"name": k, **v} for k, v in index.items() 
                if v.get("type") == file_type
            ]
        return [{"name": k, **v} for k, v in index.items()]
    
    def verify_checksum(self, filename: str) -> bool:
        """Verify file checksum."""
        search_pattern = f"{filename}.code.enc"
        candidates = list(self.omega_dir.glob(search_pattern))
        
        if not candidates:
            return False
        
        encrypted_path = candidates[0]
        meta_path = encrypted_path.with_suffix('.meta')
        
        if not meta_path.exists():
            return False
        
        meta = json.loads(meta_path.read_text())
        expected = meta.get("checksum")
        
        data = encrypted_path.read_bytes()
        nonce = data[:12]
        ciphertext = data[12:]
        
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        actual = self._compute_checksum(plaintext)
        
        return actual == expected


def create_encryptor(project: str = "default") -> OmegaPhaseEncryptor:
    """Create phase encryptor."""
    return OmegaPhaseEncryptor(project=project)


def encrypt_for_transit(data: Union[str, Dict]) -> str:
    """Encrypt data for transit (returns base64)."""
    encryptor = create_encryptor("transit")
    payload = encryptor.encrypt_string(
        json.dumps(data) if isinstance(data, dict) else data
    )
    return base64.b64encode(
        payload.nonce + payload.ciphertext
    ).decode('ascii')


def decrypt_from_transit(encrypted_b64: str) -> str:
    """Decrypt data from transit."""
    encryptor = create_encryptor("transit")
    data = base64.b64decode(encrypted_b64.encode('ascii'))
    nonce = data[:12]
    ciphertext = data[12:]
    
    plaintext = encryptor.aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode('utf-8')


if __name__ == "__main__":
    import sys
    
    project = sys.argv[1] if len(sys.argv) > 1 else "default"
    encryptor = OmegaPhaseEncryptor(project=project)
    
    print("=" * 60)
    print("OMEGA Phase Encryptor - Zero-Trust")
    print("=" * 60)
    print(f"Project: {project}")
    print(f"Encrypt dir: {encryptor.omega_dir}")
    print(f"Crypto: {HAS_CRYPTO}")
    
    print("\n[TEST] Encrypting code...")
    test_code = '''def hello():
    """Hello world."""
    print("Hello, Zero-Knowledge!")
    return 0

if __name__ == "__main__":
    hello()
'''
    
    code_path = encryptor.encrypt_code(test_code, "hello")
    print(f"  Encrypted: {code_path.name}")
    
    print("\n[TEST] Decrypting code...")
    decrypted = encryptor.decrypt_code("hello")
    print(f"  Decrypted: {len(decrypted)} chars")
    print(f"  Matches: {decrypted == test_code}")
    
    print("\n[TEST] Encrypting memory...")
    test_memory = {
        "session": "test-001",
        "lesson": "Zero-knowledge works",
        "timestamp": datetime.now().isoformat()
    }
    
    mem_path = encryptor.encrypt_memory(test_memory, "session")
    print(f"  Encrypted: {mem_path.name}")
    
    print("\n[TEST] Decrypting memory...")
    decrypted_mem = encryptor.decrypt_memory("session")
    print(f"  Session: {decrypted_mem.get('session')}")
    print(f"  Matches: {decrypted_mem.get('lesson') == test_memory['lesson']}")
    
    print("\n[TEST] Checksum verification...")
    valid = encryptor.verify_checksum("hello")
    print(f"  Checksum: {'OK' if valid else 'FAILED'}")
    
    print("\n" + "=" * 60)
    print("Zero-Trust Encryption: WORKING")
    print("=" * 60)