from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")
ALGORITHM  = "HS256"
TOKEN_TTL_HOURS = 12

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int, email: str, perfil: str) -> str:
    expire  = datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)
    payload = {"sub": str(user_id), "email": email, "perfil": perfil, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
