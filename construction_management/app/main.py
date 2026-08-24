from fastapi import FastAPI, status, Request
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.common import limiter, register_handler, StandardResponse, success_response
from app.core import settings
from app.db import Base, engine
from app.models import WorkItemModel, SiteMemberModel, ConstructionSiteModel, UserModel
from app.routers import auth_router, user_router, site_router
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Đang khởi tạo bảng...")
    Base.metadata.create_all(bind=engine)

    logger.info("Đang kiểm tra và khởi tạo dữ liệu mẫu...")
    seed_data()

    yield

    logger.info("Server đang tắt. Cảm ơn đã sử dụng!")


app = FastAPI(
    title="Project_FastAPI_construction",
    description="https://docs.google.com/spreadsheets/d/1Mc79QtR7Eoj764AqYHcdV1YmEt_SbJ5q/edit?gid=1937864429#gid=1937864429",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

register_handler(app)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(site_router)


@app.get(
    "/health",
    response_model=StandardResponse[dict[str, str]],
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="Check kết nối FastAPI",
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def health_check(request: Request) -> StandardResponse[dict[str, str]]:
    return success_response(
        request=request,
        message="FastAPI chạy tốt",
        status_code=status.HTTP_200_OK,
        data={"message": "Không có vấn đề"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
