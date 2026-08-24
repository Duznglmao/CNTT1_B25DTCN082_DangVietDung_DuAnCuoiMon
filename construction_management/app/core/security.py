from jwt import encode, decode, InvalidTokenError, ExpiredSignatureError
from pwdlib import PasswordHash
from typing import Any
from datetime import datetime, timezone, timedelta

from .config import settings
from app.exceptions import InvalidTokenException, ExpiredSignatureException

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("skibidi-password")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode |= {"exp": expire, "type": "access"}
    return encode(to_encode, settings.SECRET_KEY.get_secret_value(), settings.ALGORITHM)


def create_refresh_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode |= {"exp": expire, "type": "refresh"}
    return encode(to_encode, settings.SECRET_KEY.get_secret_value(), settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],
        )
    except ExpiredSignatureError:
        raise ExpiredSignatureException()
    except InvalidTokenError:
        raise InvalidTokenException()
