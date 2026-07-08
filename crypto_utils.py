import hashlib
import hmac
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

_key = os.environ['ENCRYPTION_KEY'].encode()
_fernet = Fernet(_key)


def encrypt_password(password: str) -> str:
    """Обратимое шифрование — нужно, чтобы бот мог реально авторизоваться на роутере."""
    return _fernet.encrypt(password.encode()).decode()


def decrypt_password(token: str) -> str:
    return _fernet.decrypt(token.encode()).decode()


def hash_password(password: str) -> str:
    """Необратимый HMAC — только для поиска дублей (совпадают ли данные у двух пользователей)."""
    return hmac.new(_key, password.encode(), hashlib.sha256).hexdigest()
