import hashlib
import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def sha256_hash(obj, length=64):
    if not isinstance(obj, bytes):
        obj = str(obj).encode("utf-8")

    _hash = hashlib.sha256(obj).hexdigest()
    return _hash[:length]


def sha256_enc(secret, password, salt=os.urandom(16)):
    if not secret or not password:
        return None

    if not isinstance(secret, bytes):
        secret = str(secret).encode("utf-8")
    if not isinstance(password, bytes):
        password = str(password).encode("utf-8")
    if not isinstance(salt, bytes):
        salt = str(salt).encode("utf-8")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend())

    cipher = Fernet(base64.urlsafe_b64encode(kdf.derive(password)))
    encrypted = cipher.encrypt(secret).decode("utf-8")
    salt = salt.decode("utf-8")

    return {"encrypted": encrypted, "salt": salt}


def sha256_dec(encrypted, password, salt):
    if not encrypted or not password or not salt:
        return None

    if not isinstance(encrypted, bytes):
        encrypted = str(encrypted).encode("utf-8")
    if not isinstance(password, bytes):
        password = str(password).encode("utf-8")
    if not isinstance(salt, bytes):
        salt = str(salt).encode("utf-8")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend())

    cipher = Fernet(base64.urlsafe_b64encode(kdf.derive(password)))
    return {"decrypted": cipher.decrypt(encrypted).decode("utf-8")}
