import os
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv

_ENV_PATH = Path(".env")
load_dotenv(dotenv_path=_ENV_PATH if _ENV_PATH.exists() else None)


def _persist_key(key: str) -> None:
    if _ENV_PATH.exists():
        content = _ENV_PATH.read_text(encoding="utf-8")
        if "FERNET_KEY" in content:
            return
        _ENV_PATH.write_text(content.rstrip() + f"\nFERNET_KEY={key}\n", encoding="utf-8")
    else:
        _ENV_PATH.write_text(f"FERNET_KEY={key}\n", encoding="utf-8")


def get_fernet() -> Fernet:
    key = os.getenv("FERNET_KEY")
    if not key:
        key = Fernet.generate_key().decode()
        _persist_key(key)
        os.environ["FERNET_KEY"] = key
    return Fernet(key.encode())
