"""
Secrets Management Module
=========================
Secure handling of sensitive data in agentic-OS

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import os
import base64
import hashlib
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class SecretsConfig:
    """Configuration for secrets management."""
    
    def __init__(self):
        self.secrets_dir = os.getenv("SECRETS_DIR", ".secrets")
        self.encryption_key_env = os.getenv("ENCRYPTION_KEY", "")
        self.vault_enabled = os.getenv("VAULT_ENABLED", "false").lower() == "true"
        self.vault_addr = os.getenv("VAULT_ADDR", "")
        self.vault_token = os.getenv("VAULT_TOKEN", "")


class SecretsManager:
    """Secure secrets management for agentic-OS."""
    
    _instance: Optional['SecretsManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = SecretsConfig()
        self._secrets_cache: Dict[str, str] = {}
        self._secrets_dir = Path(self.config.secrets_dir)
        
        # Ensure secrets directory exists
        if not self._secrets_dir.exists():
            self._secrets_dir.mkdir(parents=True, exist_ok=True)
        
        self._initialized = True
        logger.info("Secrets manager initialized")
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key."""
        key = self.config.encryption_key_env
        if not key:
            # Use a default key for development (NOT secure for production)
            key = "agentic-os-default-key-change-in-production"
        
        # Ensure key is exactly 32 bytes for AES-256
        key_hash = hashlib.sha256(key.encode()).digest()
        return key_hash
    
    def _encrypt(self, value: str) -> str:
        """Simple XOR encryption (for demonstration - use proper encryption in production)."""
        key = self._get_encryption_key()
        encrypted = bytes(a ^ b for a, b in zip(value.encode(), 
                         (key * (len(value) // len(key) + 1))[:len(value)]))
        return base64.b64encode(encrypted).decode()
    
    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt XOR encrypted value."""
        key = self._get_encryption_key()
        decoded = base64.b64decode(encrypted_value.encode())
        decrypted = bytes(a ^ b for a, b in zip(decoded, 
                         (key * (len(decoded) // len(key) + 1))[:len(decoded)]))
        return decrypted.decode()
    
    def store_secret(self, key: str, value: str, encrypt: bool = True) -> bool:
        """Store a secret securely."""
        try:
            # Store in memory cache
            self._secrets_cache[key] = value
            
            # Optionally encrypt and store to file
            if encrypt:
                encrypted = self._encrypt(value)
                secret_file = self._secrets_dir / f"{key}.secret"
                secret_file.write_text(encrypted)
            else:
                secret_file = self._secrets_dir / f"{key}.plain"
                secret_file.write_text(value)
            
            logger.info(f"Secret stored: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store secret {key}: {e}")
            return False
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret."""
        # Check memory cache first
        if key in self._secrets_cache:
            return self._secrets_cache[key]
        
        # Try to load from file
        secret_file = self._secrets_dir / f"{key}.secret"
        if secret_file.exists():
            try:
                encrypted = secret_file.read_text()
                decrypted = self._decrypt(encrypted)
                self._secrets_cache[key] = decrypted
                return decrypted
            except Exception as e:
                logger.error(f"Failed to decrypt secret {key}: {e}")
        
        # Try plain file
        plain_file = self._secrets_dir / f"{key}.plain"
        if plain_file.exists():
            try:
                value = plain_file.read_text()
                self._secrets_cache[key] = value
                return value
            except Exception as e:
                logger.error(f"Failed to read secret {key}: {e}")
        
        return default
    
    def delete_secret(self, key: str) -> bool:
        """Delete a secret."""
        try:
            # Remove from cache
            self._secrets_cache.pop(key, None)
            
            # Remove files
            for suffix in ['.secret', '.plain']:
                secret_file = self._secrets_dir / f"{key}{suffix}"
                if secret_file.exists():
                    secret_file.unlink()
            
            logger.info(f"Secret deleted: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete secret {key}: {e}")
            return False
    
    def list_secrets(self) -> list:
        """List all secret keys (not values)."""
        keys = set()
        
        for suffix in ['.secret', '.plain']:
            for f in self._secrets_dir.glob(f"*{suffix}"):
                keys.add(f.stem)
        
        return sorted(keys)
    
    def get_env_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variable."""
        return os.getenv(key, default)
    
    def rotate_secret(self, key: str, new_value: str) -> bool:
        """Rotate a secret (update with new value)."""
        return self.store_secret(key, new_value, encrypt=True)


# Environment-based secrets for common integrations
class IntegrationSecrets:
    """Helper for common integration secrets."""
    
    @staticmethod
    def get_github_token() -> Optional[str]:
        """Get GitHub token."""
        return os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
    
    @staticmethod
    def get_openai_key() -> Optional[str]:
        """Get OpenAI API key."""
        return os.getenv("OPENAI_API_KEY")
    
    @staticmethod
    def get_azure_openai_key() -> Optional[str]:
        """Get Azure OpenAI API key."""
        return os.getenv("AZURE_OPENAI_API_KEY")
    
    @staticmethod
    def get_azure_endpoint() -> Optional[str]:
        """Get Azure endpoint."""
        return os.getenv("AZURE_OPENAI_ENDPOINT")
    
    @staticmethod
    def get_anthropic_key() -> Optional[str]:
        """Get Anthropic API key."""
        return os.getenv("ANTHROPIC_API_KEY")
    
    @staticmethod
    def get_database_url() -> Optional[str]:
        """Get database connection URL."""
        return os.getenv("DATABASE_URL")
    
    @staticmethod
    def get_redis_url() -> Optional[str]:
        """Get Redis connection URL."""
        return os.getenv("REDIS_URL")
    
    @staticmethod
    def get_smtp_password() -> Optional[str]:
        """Get SMTP password."""
        return os.getenv("SMTP_PASSWORD")
    
    @staticmethod
    def get_jwt_secret() -> Optional[str]:
        """Get JWT secret key."""
        return os.getenv("JWT_SECRET")


# Global secrets manager
secrets_manager = SecretsManager()


__all__ = [
    'SecretsManager',
    'secrets_manager',
    'SecretsConfig',
    'IntegrationSecrets',
]