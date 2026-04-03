from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Header

from app.core.store import users

SECRET_KEY = "dev-secret-key-change-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def get_current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise_auth_error("JWT missing or expired")

    token = authorization.split(" ", 1)[1].strip()
    user_id = decode_token(token)
    if not user_id or user_id not in users:
        raise_auth_error("JWT missing or expired")
    return user_id


def raise_auth_error(detail: str):
    from fastapi import HTTPException
    raise HTTPException(
        status_code=401,
        detail={
            "error": {
                "code": 401,
                "message": "Unauthenticated: JWT missing or expired",
                "detail": detail,
            }
        },
    )