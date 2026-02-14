import hashlib
from passlib.context import CryptContext

# Use pbkdf2_sha256 to avoid bcrypt 72-byte limit and backend issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def password_algo() -> str:
    return "pbkdf2_sha256"


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
