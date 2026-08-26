from fastapi import APIRouter, Request, Depends, status
from typing import Annotated
from sqlalchemy.orm import Session
from loguru import logger

from app.common import StandardResponse, limiter, success_response
from app.schemas import UserCreate, UserResponse, Token, UserLogin, RefreshTokenRequest
from app.core import settings
from app.services import UserService
from app.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def register_user_endpoint(
    request: Request, user_in: UserCreate, db: Annotated[Session, Depends(get_db)]
) -> StandardResponse[UserResponse]:
    """Đăng ký tài khoản. Endpoint này dành cho người dùng chưa đăng nhập."""
    user = UserService(db).create_user(user_in)
    logger.info("Người dùng đăng ký tài khoản thành công")
    return success_response(
        request=request,
        message="Đăng ký user mới thành công!",
        status_code=status.HTTP_201_CREATED,
        data=user,
    )


@router.post(
    "/login",
    response_model=StandardResponse[Token],
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập và nhận JWT",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def login_user_endpoint(
    request: Request, user_in: UserLogin, db: Annotated[Session, Depends(get_db)]
) -> StandardResponse[Token]:
    """Đăng nhập và nhận JWT. Endpoint này dành cho người dùng chưa đăng nhập."""
    token_pair = UserService(db).login(user_in.email, user_in.password)
    logger.info("Người dùng lấy access token thành công")
    return success_response(
        request=request,
        message="Lấy access token thành công!",
        status_code=status.HTTP_200_OK,
        data=token_pair,
    )


@router.post(
    "/refresh",
    response_model=StandardResponse[Token],
    status_code=status.HTTP_200_OK,
    summary="Cấp lại access token",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def refresh_token_endpoint(
    request: Request, body: RefreshTokenRequest, db: Annotated[Session, Depends(get_db)]
) -> StandardResponse[Token]:
    """Cấp lại access token. Người có refresh token hợp lệ được phép thực hiện."""
    token_pair = UserService(db).refresh_token(body.refresh_token)
    logger.info("Người dùng lấy token mới thành công qua Refresh Token")

    return success_response(
        request=request,
        message="Lấy access token mới thành công!",
        status_code=status.HTTP_200_OK,
        data=token_pair,
    )
