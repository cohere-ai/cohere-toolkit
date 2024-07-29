import base64
import hashlib
import os
import traceback

from cryptography.fernet import Fernet

from backend.config.settings import Settings


def get_cipher() -> Fernet:
    print("get_cipher")
    # 1. Get env var
    auth_key = Settings().auth.secret_key
    # 2. Hash env var using SHA-256
    hash_digest = hashlib.sha256(auth_key.encode()).digest()
    # 3. Base64 encode hash and get 32-byte key
    fernet_key = base64.urlsafe_b64encode(hash_digest[:32])

    print("Fernet")
    return Fernet(fernet_key)


def encrypt(value: str) -> bytes:
    cipher = get_cipher()

    return cipher.encrypt(value.encode())


def decrypt(encrypted_value: bytes) -> str:
    print("decrypt")
    cipher = get_cipher()
    print(encrypted_value)
    try:
        cipher.decrypt(encrypted_value)
    except Exception as e:
        return encrypted_value.decode()
    return cipher.decrypt(encrypted_value).decode()
