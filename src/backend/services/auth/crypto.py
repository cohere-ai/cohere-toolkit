import base64
import hashlib
import os

from cryptography.fernet import Fernet


def get_cipher() -> Fernet:
    # 1. Get env var
    auth_key = os.getenv("AUTH_SECRET_KEY")
    # 2. Hash env var using SHA-256
    hash_digest = hashlib.sha256(auth_key.encode()).digest()
    # 3. Base64 encode hash and get 32-byte key
    fernet_key = base64.urlsafe_b64encode(hash_digest[:32])

    return Fernet(fernet_key)


def encrypt(value: str) -> bytes:
    cipher = get_cipher()

    return cipher.encrypt(value.encode())


def decrypt(encrypted_value: bytes) -> str:
    cipher = get_cipher()

    return cipher.decrypt(encrypted_value).decode()
