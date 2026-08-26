from fastapi import APIRouter, Request, Depends, status, Query
from typing import Annotated
from sqlalchemy.orm import Session
from loguru import logger

from app.common import StandardResponse, limiter, success_response
from app.schemas import UserResponse
from app.models import UserModel, RoleUser
from app.core import settings
from app.dependencies import get_current_active_user, RoleChecker
from app.db import get_db
from app.services import UserService

db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Xem hồ sơ cá nhân",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def get_me(
    request: Request,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """Xem hồ sơ cá nhân. Người dùng đã đăng nhập thành công được phép thực hiện."""
    logger.info("Người dùng xem thông tin tài khoản")
    return success_response(
        request=request,
        message="Xem thông tin bản thân thành công!",
        status_code=status.HTTP_200_OK,
        data=current_user,
    )


@router.get(
    "",
    response_model=StandardResponse[list[UserResponse]],
    status_code=status.HTTP_200_OK,
    summary="Danh sách/search người dùng",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def get_users(
    request: Request,
    db: db_dependency,
    current_user: Annotated[UserModel, Depends(RoleChecker(RoleUser.ADMIN))],
    search: Annotated[
        str | None, Query(description="Tìm kiếm theo email hoặc tên", max_length=100)
    ] = None,
    skip: Annotated[int, Query(ge=0, description="Bỏ qua bản ghi")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Số bản ghi tối đa")] = 20,
) -> StandardResponse[list[UserResponse]]:
    """Danh sách / tìm kiếm người dùng. Chỉ user với role Admin được phép thực hiện."""
    logger.info(f"Admin ID {current_user.id} đang lấy danh sách người dùng")
    users = UserService(db).get_users(search=search, skip=skip, limit=limit)

    return success_response(
        request=request,
        message="Lấy danh sách người dùng thành công!",
        status_code=status.HTTP_200_OK,
        data=users,
    )
