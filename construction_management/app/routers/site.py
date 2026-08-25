from fastapi import APIRouter, Request, Depends, status, Query
from typing import Annotated, Literal
from sqlalchemy.orm import Session

from app.common import StandardResponse, limiter, success_response
from app.schemas import (
    ConstructionSiteCreate,
    ConstructionSiteUpdate,
    ConstructionSiteResponse,
    SiteMemberCreate,
    SiteMemberResponse,
    WorkItemCreate,
    WorkItemResponse,
)
from app.models import UserModel, WorkItemPriority, WorkItemStatus
from app.core import settings
from app.dependencies import get_current_active_user
from app.db import get_db
from app.services import SiteService, WorkItemService

router = APIRouter(prefix="/construction-sites", tags=["Construction Sites"])


@router.post(
    "",
    response_model=StandardResponse[ConstructionSiteResponse],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def create_site_endpoint(
    request: Request,
    site_data: ConstructionSiteCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    new_site = SiteService(db).create_site(site_data, current_user)
    return success_response(
        request=request,
        message="Tạo công trình thành công!",
        status_code=status.HTTP_201_CREATED,
        data=new_site,
    )


@router.get(
    "",
    response_model=StandardResponse[list[ConstructionSiteResponse]],
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def get_sites_endpoint(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    search: str | None = Query(
        default=None, description="Tìm kiếm theo tên công trình"
    ),
):
    sites = SiteService(db).get_sites(current_user, search)
    return success_response(
        request=request, message="Lấy danh sách công trình thành công!", data=sites
    )


@router.get(
    "/{site_id}",
    response_model=StandardResponse[ConstructionSiteResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def get_site_detail_endpoint(
    request: Request,
    site_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    site_record = SiteService(db).get_site_detail(site_id, current_user)
    return success_response(
        request=request,
        message="Lấy thông tin công trình thành công!",
        data=site_record,
    )


@router.patch(
    "/{site_id}",
    response_model=StandardResponse[ConstructionSiteResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def update_site_endpoint(
    request: Request,
    site_id: int,
    update_data: ConstructionSiteUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    updated_site = SiteService(db).update_site(site_id, update_data, current_user)
    return success_response(
        request=request, message="Cập nhật công trình thành công!", data=updated_site
    )


@router.delete(
    "/{site_id}", response_model=StandardResponse[None], status_code=status.HTTP_200_OK
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def delete_site_endpoint(
    request: Request,
    site_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    SiteService(db).delete_site(site_id, current_user)
    return success_response(
        request=request,
        message="Đã xóa công trình!",
    )


@router.post(
    "/{site_id}/members",
    response_model=StandardResponse[SiteMemberResponse],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def add_member_endpoint(
    request: Request,
    site_id: int,
    member_data: SiteMemberCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    new_member = SiteService(db).add_member(site_id, member_data, current_user)
    return success_response(
        request=request,
        message="Thêm thành viên thành công!",
        status_code=status.HTTP_201_CREATED,
        data=new_member,
    )


@router.delete(
    "/{site_id}/members/{user_id}",
    response_model=StandardResponse[None],
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def remove_member_endpoint(
    request: Request,
    site_id: int,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    SiteService(db).remove_member(site_id, user_id, current_user)
    return success_response(
        request=request, message="Xóa thành viên khỏi công trình thành công!"
    )


@router.get(
    "/{site_id}/members",
    response_model=StandardResponse[list[SiteMemberResponse]],
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def get_members_endpoint(
    request: Request,
    site_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    members = SiteService(db).get_members(site_id, current_user)
    return success_response(
        request=request, message="Lấy danh sách thành viên thành công!", data=members
    )


@router.post("/{site_id}/work-items", response_model=StandardResponse[WorkItemResponse])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def create_work_item_endpoint(
    request: Request,
    site_id: int,
    data: WorkItemCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    item = WorkItemService(db).create_work_item(site_id, data, current_user)
    return success_response(
        request=request, message="Tạo công việc thành công!", data=item
    )


@router.get(
    "/{site_id}/work-items", response_model=StandardResponse[list[WorkItemResponse]]
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def get_work_items_endpoint(
    request: Request,
    site_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    status: WorkItemStatus | None = Query(None),
    priority: WorkItemPriority | None = Query(None),
    assignee_id: int | None = Query(None),
    search: str | None = Query(None, description="Tìm theo tên công việc"),
    sort_by: Literal["created_at", "due_date"] = Query("created_at"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    items = WorkItemService(db).get_work_items(
        site_id,
        current_user,
        status,
        priority,
        assignee_id,
        search,
        sort_by,
        skip,
        limit,
    )
    return success_response(
        request=request, message="Lấy danh sách công việc!", data=items
    )
