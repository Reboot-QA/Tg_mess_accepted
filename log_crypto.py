"""日志行加密（AES-256-GCM），仅用于写入磁盘的日志文件。"""

from __future__ import annotations

import base64
import logging
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_MAGIC = b"LG1"
_SALT_LEN = 16
_NONCE_LEN = 12
_KDF_ITERS = 480_000


def _derive_key(secret: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_KDF_ITERS,
    )
    return kdf.derive(secret.encode("utf-8"))


def encrypt_line(plaintext: str, secret: str) -> str:
    salt = os.urandom(_SALT_LEN)
    key = _derive_key(secret, salt)
    nonce = os.urandom(_NONCE_LEN)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), _MAGIC)
    blob = _MAGIC + salt + nonce + ciphertext
    return base64.urlsafe_b64encode(blob).decode("ascii")


def decrypt_line(token: str, secret: str) -> str:
    raw = token.strip()
    if raw.upper().startswith("ENC:"):
        raw = raw[4:].strip()
    blob = base64.urlsafe_b64decode(raw.encode("ascii"))
    if not blob.startswith(_MAGIC):
        raise ValueError("无效的日志密文")
    offset = len(_MAGIC)
    salt = blob[offset : offset + _SALT_LEN]
    offset += _SALT_LEN
    nonce = blob[offset : offset + _NONCE_LEN]
    offset += _NONCE_LEN
    ciphertext = blob[offset:]
    key = _derive_key(secret, salt)
    plain = AESGCM(key).decrypt(nonce, ciphertext, _MAGIC)
    return plain.decode("utf-8")


class EncryptedFileHandler(logging.Handler):
    def __init__(self, path: Path, secret: str) -> None:
        super().__init__()
        self._path = path
        self._secret = secret
        path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            line = encrypt_line(self.format(record), self._secret)
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(f"ENC:{line}\n")
        except Exception:
            self.handleError(record)
