from fastapi import Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db import get_db
from app.services import UserService
from app.models import UserModel, RoleUser
from app.core import decode_token
from app.exceptions import InvalidTokenException, UserNotFoundError, InactiveUserError

http_bearer_scheme = HTTPBearer(
    scheme_name="jwt bearer", description="Mời nhập vào Token"
)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> UserModel:
    user_service = UserService(db)
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise InvalidTokenException()

    user_email = payload.get("sub", None)
    if not user_email:
        raise InvalidTokenException()

    user = user_service.get_by_email(user_email)
    if not user:
        raise UserNotFoundError(user_email)

    return user


def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserModel:
    if not current_user.is_active:
        raise InactiveUserError()
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: list[RoleUser]):
        self.allowed_roles = allowed_roles

    def __call__(
        self, current_user: Annotated[UserModel, Depends(get_current_active_user)]
    ):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện thao tác này",
            )
        return current_user
