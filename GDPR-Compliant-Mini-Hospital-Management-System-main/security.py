from __future__ import annotations

import hashlib
from typing import Optional

from config import get_fernet

_fernet = get_fernet()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def encrypt_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return _fernet.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return _fernet.decrypt(value.encode("utf-8")).decode("utf-8")


def mask_name(patient_id: int) -> str:
    return f"ANON_{patient_id:04d}"


def mask_contact(contact: Optional[str]) -> str:
    if not contact:
        return "XXX-XXX-XXXX"
    digits = "".join(ch for ch in contact if ch.isdigit())
    visible = digits[-4:].rjust(4, "X")
    return f"XXX-XXX-{visible}"


def mask_text(value: Optional[str]) -> str:
    if not value:
        return "REDACTED"
    return value.split()[0][:3].upper() + "***"
