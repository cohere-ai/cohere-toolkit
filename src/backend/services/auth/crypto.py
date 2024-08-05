import base64
import hashlib

from cryptography.fernet import Fernet

from backend.config.settings import Settings


def get_cipher() -> Fernet:
    """
    Utility method to retrieve the Fernet Cipher and using the config auth secret key for encryption/decryption.
    """

    # 1. Get env var
    auth_key = Settings().auth.secret_key
    # 2. Hash env var using SHA-256
    hash_digest = hashlib.sha256(auth_key.encode()).digest()
    # 3. Base64 encode hash and get 32-byte key
    fernet_key = base64.urlsafe_b64encode(hash_digest[:32])

    return Fernet(fernet_key)


def encrypt(value: str) -> bytes:
    """
    Utility method to encrypt a string value using a Fernet Cipher.
    """
    cipher = get_cipher()

    return cipher.encrypt(value.encode())


def decrypt(encrypted_value: bytes) -> str:
    """
    Utility method to decrypt a string value using a Fernet Cipher.
    """
    cipher = get_cipher()

    return cipher.decrypt(encrypted_value).decode()


def convert_string_encryption_to_cipher_encryption(encoded_value: bytes):
    """
    Utility method to convert old string encodings into Fernet Cipher encryptions.
    """
    decoded = encoded_value.decode()

    return encrypt(decoded)
