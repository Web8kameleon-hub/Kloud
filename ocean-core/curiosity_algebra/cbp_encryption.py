# -*- coding: utf-8 -*-
"""
🔐 KLOUD BINARY PROTOCOL - AES-GCM ENCRYPTION LAYER
=======================================================

Enterprise-grade encryption for CBP protocol.

Frame Layout me encryption:
    CLSN | ver | flags(ENCRYPTED) | payload_len | encrypted_payload
    
Encrypted Payload:
    nonce (12 bytes) | ciphertext | tag (16 bytes)

Features:
- AES-256-GCM authenticated encryption
- Per-frame nonce generation
- Key derivation with HKDF
- Automatic key rotation support

Author: Kloud Team
"""

import os
import struct
import hashlib
import hmac
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

# Try to import cryptography library
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


# ==================== CONSTANTS ====================

NONCE_SIZE = 12      # GCM standard nonce size
TAG_SIZE = 16        # GCM tag size
KEY_SIZE = 32        # AES-256 key size
SALT_SIZE = 16       # Salt for HKDF


class EncryptionError(Exception):
    """Encryption error"""
    pass


class DecryptionError(Exception):
    """Decryption error"""
    pass


@dataclass
class EncryptedPayload:
    """Encrypted payload structure"""
    nonce: bytes           # 12 bytes
    ciphertext: bytes      # Variable length
    tag: bytes             # 16 bytes (included in ciphertext by AESGCM)
    
    def to_bytes(self) -> bytes:
        """Serialize to bytes: nonce + ciphertext_with_tag"""
        return self.nonce + self.ciphertext
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'EncryptedPayload':
        """Deserialize from bytes"""
        if len(data) < NONCE_SIZE + TAG_SIZE:
            raise DecryptionError("Encrypted payload too short")
        
        nonce = data[:NONCE_SIZE]
        ciphertext = data[NONCE_SIZE:]  # Includes tag
        tag = ciphertext[-TAG_SIZE:]    # Last 16 bytes
        
        return cls(nonce=nonce, ciphertext=ciphertext, tag=tag)


class CbpEncryption:
    """
    AES-256-GCM Encryption for Kloud Binary Protocol
    
    Usage:
        enc = CbpEncryption(master_key)
        encrypted = enc.encrypt(plaintext)
        decrypted = enc.decrypt(encrypted)
    """
    
    def __init__(self, key: bytes, info: bytes = b"kloud-cbp-v1"):
        """
        Initialize encryption with master key
        
        Args:
            key: Master key (any length, will be derived to 32 bytes)
            info: Context info for key derivation
        """
        if not HAS_CRYPTO:
            raise ImportError("cryptography library required: pip install cryptography")
        
        # Derive key using HKDF
        self.key = self._derive_key(key, info)
        self.aesgcm = AESGCM(self.key)
        
        # Stats
        self.encrypted_count = 0
        self.decrypted_count = 0
        self.bytes_encrypted = 0
        self.bytes_decrypted = 0
    
    def _derive_key(self, master_key: bytes, info: bytes) -> bytes:
        """Derive encryption key using HKDF"""
        if len(master_key) == KEY_SIZE:
            return master_key
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=KEY_SIZE,
            salt=b"kloud-salt-v1",
            info=info,
            backend=default_backend()
        )
        return hkdf.derive(master_key)
    
    def encrypt(self, plaintext: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Encrypt plaintext with AES-256-GCM
        
        Args:
            plaintext: Data to encrypt
            associated_data: Additional authenticated data (header)
        
        Returns:
            nonce (12 bytes) + ciphertext + tag (16 bytes)
        """
        # Generate random nonce
        nonce = os.urandom(NONCE_SIZE)
        
        # Encrypt with authentication
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, associated_data)
        
        # Update stats
        self.encrypted_count += 1
        self.bytes_encrypted += len(plaintext)
        
        # Return nonce + ciphertext (tag is appended by AESGCM)
        return nonce + ciphertext
    
    def decrypt(self, encrypted_data: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt AES-256-GCM encrypted data
        
        Args:
            encrypted_data: nonce + ciphertext + tag
            associated_data: Additional authenticated data (must match encryption)
        
        Returns:
            Decrypted plaintext
        """
        if len(encrypted_data) < NONCE_SIZE + TAG_SIZE:
            raise DecryptionError("Encrypted data too short")
        
        # Extract nonce and ciphertext
        nonce = encrypted_data[:NONCE_SIZE]
        ciphertext = encrypted_data[NONCE_SIZE:]
        
        try:
            # Decrypt and verify
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, associated_data)
            
            # Update stats
            self.decrypted_count += 1
            self.bytes_decrypted += len(plaintext)
            
            return plaintext
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {e}")
    
    def encrypt_frame_payload(self, payload: bytes, header: bytes) -> bytes:
        """
        Encrypt CBP frame payload with header as AAD
        
        Args:
            payload: Plain payload bytes
            header: CBP header (8 bytes) - used as additional authenticated data
        
        Returns:
            Encrypted payload bytes
        """
        return self.encrypt(payload, associated_data=header)
    
    def decrypt_frame_payload(self, encrypted_payload: bytes, header: bytes) -> bytes:
        """
        Decrypt CBP frame payload with header as AAD
        
        Args:
            encrypted_payload: Encrypted payload bytes
            header: CBP header (8 bytes) - must match encryption
        
        Returns:
            Decrypted payload bytes
        """
        return self.decrypt(encrypted_payload, associated_data=header)
    
    def get_stats(self) -> dict:
        """Get encryption statistics"""
        return {
            "encrypted_count": self.encrypted_count,
            "decrypted_count": self.decrypted_count,
            "bytes_encrypted": self.bytes_encrypted,
            "bytes_decrypted": self.bytes_decrypted,
            "key_size": KEY_SIZE * 8,
            "algorithm": "AES-256-GCM"
        }


class CbpKeyManager:
    """
    Key management for CBP encryption
    
    Features:
    - Key derivation from password
    - Key rotation
    - Multiple key slots
    """
    
    def __init__(self):
        self.keys: dict[str, bytes] = {}
        self.active_key_id: Optional[str] = None
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Derive key from password using PBKDF2
        
        Returns:
            (key, salt)
        """
        if salt is None:
            salt = os.urandom(SALT_SIZE)
        
        # Use hashlib for PBKDF2
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations=100000,
            dklen=KEY_SIZE
        )
        
        return key, salt
    
    def add_key(self, key_id: str, key: bytes):
        """Add key to manager"""
        if len(key) != KEY_SIZE:
            raise ValueError(f"Key must be {KEY_SIZE} bytes")
        self.keys[key_id] = key
        if self.active_key_id is None:
            self.active_key_id = key_id
    
    def set_active_key(self, key_id: str):
        """Set active key"""
        if key_id not in self.keys:
            raise KeyError(f"Key not found: {key_id}")
        self.active_key_id = key_id
    
    def get_active_key(self) -> Optional[bytes]:
        """Get active key"""
        if self.active_key_id is None:
            return None
        return self.keys.get(self.active_key_id)
    
    def get_encryptor(self, key_id: Optional[str] = None) -> CbpEncryption:
        """Get encryptor for key"""
        if key_id is None:
            key_id = self.active_key_id
        if key_id is None:
            raise ValueError("No active key")
        
        key = self.keys.get(key_id)
        if key is None:
            raise KeyError(f"Key not found: {key_id}")
        
        return CbpEncryption(key)
    
    def rotate_key(self, new_key: bytes) -> str:
        """
        Rotate to new key
        
        Returns:
            New key ID
        """
        key_id = f"key-{len(self.keys) + 1}"
        self.add_key(key_id, new_key)
        self.set_active_key(key_id)
        return key_id


# ==================== FALLBACK (No cryptography) ====================

class SimpleCbpEncryption:
    """
    Simple XOR-based encryption fallback (NOT SECURE - for testing only!)
    Use CbpEncryption with cryptography library for production.
    """
    
    def __init__(self, key: bytes):
        self.key = hashlib.sha256(key).digest()
        self.encrypted_count = 0
        self.decrypted_count = 0
    
    def encrypt(self, plaintext: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """Simple XOR encryption (NOT SECURE)"""
        nonce = os.urandom(NONCE_SIZE)
        
        # Derive stream key from nonce + key
        stream_key = hashlib.sha256(nonce + self.key).digest()
        
        # XOR encrypt
        ciphertext = bytes([
            plaintext[i] ^ stream_key[i % len(stream_key)]
            for i in range(len(plaintext))
        ])
        
        # Simple MAC
        mac = hmac.new(self.key, nonce + ciphertext, hashlib.sha256).digest()[:TAG_SIZE]
        
        self.encrypted_count += 1
        return nonce + ciphertext + mac
    
    def decrypt(self, encrypted_data: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """Simple XOR decryption (NOT SECURE)"""
        if len(encrypted_data) < NONCE_SIZE + TAG_SIZE:
            raise DecryptionError("Data too short")
        
        nonce = encrypted_data[:NONCE_SIZE]
        ciphertext = encrypted_data[NONCE_SIZE:-TAG_SIZE]
        mac = encrypted_data[-TAG_SIZE:]
        
        # Verify MAC
        expected_mac = hmac.new(self.key, nonce + ciphertext, hashlib.sha256).digest()[:TAG_SIZE]
        if not hmac.compare_digest(mac, expected_mac):
            raise DecryptionError("MAC verification failed")
        
        # Derive stream key
        stream_key = hashlib.sha256(nonce + self.key).digest()
        
        # XOR decrypt
        plaintext = bytes([
            ciphertext[i] ^ stream_key[i % len(stream_key)]
            for i in range(len(ciphertext))
        ])
        
        self.decrypted_count += 1
        return plaintext
    
    def get_stats(self) -> dict:
        return {
            "encrypted_count": self.encrypted_count,
            "decrypted_count": self.decrypted_count,
            "algorithm": "XOR-HMAC (NOT SECURE - testing only)",
            "warning": "Install cryptography library for AES-GCM"
        }


# ==================== FACTORY ====================

def get_encryption(key: bytes) -> CbpEncryption:
    """
    Get best available encryption
    
    Returns CbpEncryption if cryptography is available,
    otherwise SimpleCbpEncryption (with warning)
    """
    if HAS_CRYPTO:
        return CbpEncryption(key)
    else:
        import warnings
        warnings.warn(
            "cryptography library not installed. Using insecure fallback. "
            "Install with: pip install cryptography",
            RuntimeWarning
        )
        return SimpleCbpEncryption(key)


# Global key manager
_key_manager: Optional[CbpKeyManager] = None


def get_key_manager() -> CbpKeyManager:
    """Get global key manager"""
    global _key_manager
    if _key_manager is None:
        _key_manager = CbpKeyManager()
    return _key_manager


# ==================== TESTING ====================

if __name__ == "__main__":
    print("🔐 Kloud CBP Encryption Test")
    print("=" * 40)
    
    # Test key
    key = b"kloud-secret-key-2026"
    
    # Get encryption
    enc = get_encryption(key)
    print(f"Algorithm: {enc.get_stats().get('algorithm', 'unknown')}")
    
    # Test encrypt/decrypt
    plaintext = b"Hello, Kloud! This is a test message."
    print(f"\nPlaintext: {plaintext}")
    
    encrypted = enc.encrypt(plaintext)
    print(f"Encrypted: {encrypted[:20].hex()}... ({len(encrypted)} bytes)")
    
    decrypted = enc.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    assert decrypted == plaintext, "Decryption failed!"
    print("\n✅ Encryption test passed!")
    
    # Test with AAD (header)
    header = b"CLSN\x01\x02\x00\x20"  # Example CBP header
    
    encrypted_with_aad = enc.encrypt(plaintext, associated_data=header)
    decrypted_with_aad = enc.decrypt(encrypted_with_aad, associated_data=header)
    
    assert decrypted_with_aad == plaintext, "AAD decryption failed!"
    print("✅ AAD encryption test passed!")
    
    # Print stats
    print(f"\nStats: {enc.get_stats()}")

