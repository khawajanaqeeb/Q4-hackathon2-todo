import os
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidTag
import base64
from typing import Tuple, Optional


class CryptoUtils:
    """Encryption utilities for secure API key management."""

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes) -> bytes:
        """
        Derive an encryption key from a password and salt using PBKDF2.

        Args:
            password: Password to derive key from
            salt: Salt for key derivation

        Returns:
            Derived encryption key (32 bytes for AES-256)
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key for AES-256
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())

    @staticmethod
    def generate_salt(length: int = 16) -> bytes:
        """
        Generate a random salt for key derivation.

        Args:
            length: Length of salt in bytes (default 16 bytes = 128 bits)

        Returns:
            Random salt
        """
        return secrets.token_bytes(length)

    @staticmethod
    def generate_iv(length: int = 16) -> bytes:
        """
        Generate a random initialization vector.

        Args:
            length: Length of IV in bytes (default 16 bytes = 128 bits)

        Returns:
            Random IV
        """
        return secrets.token_bytes(length)

    @staticmethod
    def encrypt_data(data: str, password: str) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt data using AES-256-GCM.

        Args:
            data: String data to encrypt
            password: Password for encryption

        Returns:
            Tuple of (encrypted_data, iv, salt)
        """
        # Generate salt and IV
        salt = CryptoUtils.generate_salt()
        iv = CryptoUtils.generate_iv()

        # Derive key from password and salt
        key = CryptoUtils.derive_key_from_password(password, salt)

        # Create cipher and encrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()

        encrypted_data = encryptor.update(data.encode()) + encryptor.finalize()

        # The authentication tag is included in the finalize() result for GCM mode
        # For simplicity, we'll return the tag separately if needed
        return encrypted_data, iv, salt

    @staticmethod
    def decrypt_data(encrypted_data: bytes, iv: bytes, salt: bytes, password: str) -> str:
        """
        Decrypt data using AES-256-GCM.

        Args:
            encrypted_data: Encrypted data
            iv: Initialization vector used for encryption
            salt: Salt used for key derivation
            password: Password for decryption

        Returns:
            Decrypted string data
        """
        # Derive key from password and salt
        key = CryptoUtils.derive_key_from_password(password, salt)

        # Create cipher and decrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        return decrypted_data.decode()

    @staticmethod
    def encrypt_api_key(api_key: str, encryption_password: Optional[str] = None) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt an API key using the system's encryption password.

        Args:
            api_key: API key to encrypt
            encryption_password: Password for encryption (defaults to ENCRYPTION_PASSWORD env var)

        Returns:
            Tuple of (encrypted_key, iv, salt)
        """
        password = (
            encryption_password or
            os.getenv("ENCRYPTION_PASSWORD") or
            "default-encryption-password-change-in-production"
        )

        return CryptoUtils.encrypt_data(api_key, password)

    @staticmethod
    def decrypt_api_key(encrypted_key: bytes, iv: bytes, salt: bytes, encryption_password: Optional[str] = None) -> str:
        """
        Decrypt an API key using the system's encryption password.

        Args:
            encrypted_key: Encrypted API key
            iv: Initialization vector
            salt: Salt used for encryption
            encryption_password: Password for decryption (defaults to ENCRYPTION_PASSWORD env var)

        Returns:
            Decrypted API key
        """
        password = (
            encryption_password or
            os.getenv("ENCRYPTION_PASSWORD") or
            "default-encryption-password-change-in-production"
        )

        return CryptoUtils.decrypt_data(encrypted_key, iv, salt, password)

    @staticmethod
    def hash_data(data: str, algorithm: str = "sha256") -> str:
        """
        Hash data using the specified algorithm.

        Args:
            data: Data to hash
            algorithm: Hash algorithm to use ('sha256', 'sha512')

        Returns:
            Hex-encoded hash of the data
        """
        if algorithm.lower() == "sha256":
            digest = hashes.Hash(hashes.SHA256())
        elif algorithm.lower() == "sha512":
            digest = hashes.Hash(hashes.SHA512())
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        digest.update(data.encode())
        return digest.finalize().hex()

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a cryptographically secure random token.

        Args:
            length: Length of token in bytes (default 32 bytes = 256 bits)

        Returns:
            URL-safe base64 encoded token
        """
        token_bytes = secrets.token_bytes(length)
        return base64.urlsafe_b64encode(token_bytes).decode('utf-8')

    @staticmethod
    def verify_hash(data: str, expected_hash: str, algorithm: str = "sha256") -> bool:
        """
        Verify that the hash of the data matches the expected hash.

        Args:
            data: Data to hash and compare
            expected_hash: Expected hash to compare against
            algorithm: Hash algorithm to use

        Returns:
            True if hashes match, False otherwise
        """
        computed_hash = CryptoUtils.hash_data(data, algorithm)
        return secrets.compare_digest(computed_hash, expected_hash)