from fastapi import APIRouter, Request, Depends, status, UploadFile, File
from typing import Annotated
from sqlalchemy.orm import Session

from app.common import StandardResponse, success_response, limiter
from app.core import settings
from app.schemas.work_item import WorkItemUpdate, WorkItemDetailResponse
from app.models import UserModel
from app.dependencies import get_current_active_user
from app.db import get_db
from app.services.work_item import WorkItemService

router = APIRouter(prefix="/work-items", tags=["Work Items"])


@router.patch("/{item_id}", response_model=StandardResponse[WorkItemDetailResponse])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def update_work_item_endpoint(
    request: Request,
    item_id: int,
    update_data: WorkItemUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    item = WorkItemService(db).update_work_item(item_id, update_data, current_user)
    return success_response(request=request, message="Cập nhật thành công!", data=item)


@router.post("/{item_id}/attachments")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def upload_file_endpoint(
    request: Request,
    item_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    file: UploadFile = File(...),
):
    attachment = WorkItemService(db).upload_attachment(item_id, file, current_user)
    return success_response(
        request=request,
        message="Tải file lên thành công!",
        data={"file_name": attachment.file_name, "file_path": attachment.file_path},
    )


@router.get("/{item_id}", response_model=StandardResponse[WorkItemDetailResponse])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def get_work_item_endpoint(
    request: Request,
    item_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    item = WorkItemService(db).get_work_item_detail(item_id, current_user)
    return success_response(
        request=request, message="Lấy chi tiết thành công!", data=item
    )


@router.delete("/{item_id}", response_model=StandardResponse[None])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def delete_work_item_endpoint(
    request: Request,
    item_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    WorkItemService(db).delete_work_item(item_id, current_user)
    return success_response(request=request, message="Xóa hạng mục thành công!")
