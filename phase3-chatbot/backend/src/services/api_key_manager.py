import os
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidTag
import secrets
import base64
from ..models.api_key import ApiKey


class ApiKeyManager:
    """Secure management of user API keys with AES-256 encryption."""

    def __init__(self, encryption_password: Optional[str] = None):
        """
        Initialize the API Key Manager.

        Args:
            encryption_password: Password for encrypting/decrypting API keys.
                               If not provided, will use ENCRYPTION_PASSWORD env var.
        """
        self.encryption_password = (
            encryption_password or
            os.getenv("ENCRYPTION_PASSWORD") or
            "default-encryption-password-change-in-production"
        ).encode()

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive an encryption key from the password and salt.

        Args:
            salt: Salt for key derivation

        Returns:
            Derived encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key for AES-256
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(self.encryption_password)

    def _generate_salt(self) -> bytes:
        """Generate a random salt for key derivation."""
        return secrets.token_bytes(16)

    def _generate_iv(self) -> bytes:
        """Generate a random initialization vector."""
        return secrets.token_bytes(16)

    def encrypt_key(self, api_key: str) -> tuple[bytes, bytes, bytes]:
        """
        Encrypt an API key using AES-256-GCM.

        Args:
            api_key: The API key to encrypt

        Returns:
            Tuple of (encrypted_key, iv, salt)
        """
        # Generate salt and IV
        salt = self._generate_salt()
        iv = self._generate_iv()

        # Derive key from password and salt
        key = self._derive_key(salt)

        # Create cipher and encrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()

        encrypted_data = encryptor.update(api_key.encode()) + encryptor.finalize()

        return encrypted_data, iv, salt

    def decrypt_key(self, encrypted_key: bytes, iv: bytes, salt: bytes) -> str:
        """
        Decrypt an API key using AES-256-GCM.

        Args:
            encrypted_key: The encrypted API key
            iv: Initialization vector used for encryption
            salt: Salt used for key derivation

        Returns:
            Decrypted API key string
        """
        # Derive key from password and salt
        key = self._derive_key(salt)

        # Create cipher and decrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(encrypted_key) + decryptor.finalize()

        return decrypted_data.decode()

    def store_key(
        self,
        session: Session,
        user_id: str,
        provider: str,
        api_key: str,
        expires_at: Optional[datetime] = None
    ) -> ApiKey:
        """
        Store an encrypted API key in the database.

        Args:
            session: Database session
            user_id: User ID associated with the key
            provider: Provider name (e.g., 'openai', 'anthropic')
            api_key: Raw API key to encrypt and store
            expires_at: Optional expiration datetime

        Returns:
            Created ApiKey object
        """
        # Encrypt the API key
        encrypted_key, iv, salt = self.encrypt_key(api_key)

        # Create the API key object
        db_api_key = ApiKey(
            provider=provider,
            user_id=user_id,
            encrypted_key=encrypted_key,
            encrypted_key_iv=iv,
            encrypted_key_salt=salt,
            expires_at=expires_at
        )

        # Add to database
        session.add(db_api_key)
        session.commit()
        session.refresh(db_api_key)

        return db_api_key

    def retrieve_key(
        self,
        session: Session,
        user_id: str,
        provider: str
    ) -> Optional[str]:
        """
        Retrieve and decrypt an API key for a user and provider.

        Args:
            session: Database session
            user_id: User ID
            provider: Provider name

        Returns:
            Decrypted API key string or None if not found
        """
        # Query for the API key
        statement = select(ApiKey).where(
            ApiKey.user_id == user_id,
            ApiKey.provider == provider,
            ApiKey.is_active == True
        )
        db_api_key = session.exec(statement).first()

        if not db_api_key:
            return None

        # Check if the key has expired
        if db_api_key.expires_at and db_api_key.expires_at < datetime.utcnow():
            # Mark as inactive
            db_api_key.is_active = False
            session.add(db_api_key)
            session.commit()
            return None

        # Decrypt and return the key
        try:
            decrypted_key = self.decrypt_key(
                db_api_key.encrypted_key,
                db_api_key.encrypted_key_iv,
                db_api_key.encrypted_key_salt
            )
            return decrypted_key
        except InvalidTag:
            # Decryption failed, possibly due to wrong password
            return None

    def validate_key(self, api_key: str) -> bool:
        """
        Validate the format of an API key.

        Args:
            api_key: API key to validate

        Returns:
            True if valid format, False otherwise
        """
        # Basic validation - check if it looks like a typical API key
        # This is a basic check - implement provider-specific validation as needed
        if not api_key or len(api_key) < 10:
            return False

        # Most API keys start with 'sk-' or similar prefixes
        # Customize this based on specific provider requirements
        return True

    def rotate_key(
        self,
        session: Session,
        user_id: str,
        provider: str,
        new_api_key: str
    ) -> bool:
        """
        Rotate an existing API key with a new one.

        Args:
            session: Database session
            user_id: User ID
            provider: Provider name
            new_api_key: New API key to store

        Returns:
            True if successful, False otherwise
        """
        # First, validate the new key
        if not self.validate_key(new_api_key):
            return False

        # Find the existing key
        statement = select(ApiKey).where(
            ApiKey.user_id == user_id,
            ApiKey.provider == provider,
            ApiKey.is_active == True
        )
        db_api_key = session.exec(statement).first()

        if not db_api_key:
            return False

        # Encrypt the new key
        encrypted_key, iv, salt = self.encrypt_key(new_api_key)

        # Update the existing key
        db_api_key.encrypted_key = encrypted_key
        db_api_key.encrypted_key_iv = iv
        db_api_key.encrypted_key_salt = salt
        db_api_key.created_at = datetime.utcnow()

        session.add(db_api_key)
        session.commit()

        return True