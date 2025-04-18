from uuid import UUID
from jose import jwt, JWTError
from datetime import datetime, timedelta
from decouple import config

JWT_SECRET = config("JWT_SECRET")
JWT_ALG= config("JWT_ALG")
JWT_ACCESS_TOKEN_EXP = config("JWT_ACCESS_TOKEN_EXP", cast=int)
JWT_REFRESH_TOKEN_EXP = config("JWT_REFRESH_TOKEN_EXP", cast=int)

def create_token(user_id: UUID, role: str, expires_delta: timedelta, token_type: str = "access"):
    payload = {
        "sub": str(user_id),
        "role": role,
    }
    expire = datetime.now() + expires_delta
    payload.update({"exp": expire})
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def create_access_token(user_id: UUID, role: str):
    return create_token(user_id, role, timedelta(minutes=JWT_ACCESS_TOKEN_EXP), "access")

def create_refresh_token(user_id: UUID, role: str):
    return create_token(user_id, role, timedelta(days=JWT_REFRESH_TOKEN_EXP), "refresh")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload
    except JWTError:
        return None
