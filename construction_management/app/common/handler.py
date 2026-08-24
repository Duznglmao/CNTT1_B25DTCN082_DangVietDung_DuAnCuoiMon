from fastapi import HTTPException, Request, status, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from slowapi.errors import RateLimitExceeded

from .response import error_response
from loguru import logger
from app.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(f"[AppException] {request.url.path} | {exc.message}")
    return error_response(
        request=request,
        message=exc.message,
        status_code=exc.status_code,
        error=exc.error_code,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(f"[HTTP {exc.status_code}] {request.url.path} | {exc.detail}")
    return error_response(
        request=request,
        message=str(exc.detail) if isinstance(exc.detail, str) else "Lỗi yêu cầu HTTP",
        status_code=exc.status_code,
        error=exc.detail,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(f"[ValidationError] {request.url.path} | {exc.errors()}")
    return error_response(
        request=request,
        message="Dữ liệu đầu vào không hợp lệ!",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error=exc.errors(),
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    logger.warning(f"[RateLimitExceeded] {request.url.path} | Detail: {exc.detail}")
    return error_response(
        request=request,
        message="Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau!",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        error="RATE_LIMIT_EXCEEDED",
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    logger.warning(f"[ValueError] {request.url.path} | {exc}")
    return error_response(
        request=request,
        message="Dữ liệu không hợp lệ hoặc bị trùng!",
        status_code=status.HTTP_400_BAD_REQUEST,
        error="VALUE_ERROR",
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    logger.error(f"[IntegrityError] {request.url.path} | Detail : {exc.orig}")
    return error_response(
        request=request,
        message="Lỗi vi phạm ràng buộc cơ sở dữ liệu!",
        status_code=status.HTTP_400_BAD_REQUEST,
        error="INTEGRITY_ERROR",
    )


async def sqlalchemy_error_handler(
    request: Request, _: SQLAlchemyError
) -> JSONResponse:
    logger.exception(f"[DatabaseError] {request.url.path}")
    return error_response(
        request=request,
        message="Lỗi truy vấn cơ sở dữ liệu!",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="DATABASE_ERROR",
    )


async def general_exception_handler(request: Request, _: Exception) -> JSONResponse:
    logger.exception(f"[UnhandledError] {request.url.path}")
    return error_response(
        request=request,
        message="Hệ thống gặp sự cố! Vui lòng thử lại sau!",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="INTERNAL_SERVER_ERROR",
    )


def register_handler(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
