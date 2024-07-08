import base64
import os

from cryptography.fernet import Fernet


def get_cipher() -> Fernet:
    key = base64.urlsafe_b64encode(os.environ.get("AUTH_SECRET_KEY").encode())
    return Fernet(key)


def encrypt(value: str) -> bytes:
    cipher = get_cipher()

    return cipher.encrypt(value.encode())


def decrypt(encrypted_value: bytes) -> str:
    cipher = get_cipher()

    return cipher.decrypt(encrypted_value).decode()
