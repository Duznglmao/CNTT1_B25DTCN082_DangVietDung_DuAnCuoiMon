import os
import uuid
import shutil
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models import (
    WorkItemModel,
    SiteMemberModel,
    ConstructionSiteModel,
    UserModel,
    MemberRole,
    WorkItemAttachmentModel,
)
from app.schemas.work_item import WorkItemCreate, WorkItemUpdate

from app.exceptions import (
    PermissionDeniedError,
    InvalidAssigneeError,
    WorkItemNotFoundError,
    InvalidFileTypeError,
    FileTooLargeError,
)


class WorkItemService:
    def __init__(self, db: Session):
        self.db = db

    def _check_site_membership(self, site_id: int, user_id: int) -> SiteMemberModel:
        member = (
            self.db.query(SiteMemberModel)
            .join(ConstructionSiteModel)
            .filter(
                SiteMemberModel.site_id == site_id,
                SiteMemberModel.user_id == user_id,
                ConstructionSiteModel.is_deleted == False,
            )
            .first()
        )
        if not member:
            raise PermissionDeniedError(
                "Công trường không tồn tại hoặc bạn không có quyền truy cập!"
            )
        return member

    def _validate_assignee(self, site_id: int, assignee_id: int):
        is_member = (
            self.db.query(SiteMemberModel)
            .filter(
                SiteMemberModel.site_id == site_id,
                SiteMemberModel.user_id == assignee_id,
            )
            .first()
        )
        if not is_member:
            raise InvalidAssigneeError() 

    def create_work_item(
        self, site_id: int, data: WorkItemCreate, current_user: UserModel
    ) -> WorkItemModel:
        self._check_site_membership(site_id, current_user.id)

        if data.assignee_id:
            self._validate_assignee(site_id, data.assignee_id)

        item = WorkItemModel(site_id=site_id, **data.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_work_items(
        self,
        site_id: int,
        current_user: UserModel,
        status: str = None,
        priority: str = None,
        assignee_id: int = None,
        search: str = None,
        sort_by: str = "created_at",
        skip: int = 0,
        limit: int = 20,
    ) -> list[WorkItemModel]:
        self._check_site_membership(site_id, current_user.id)

        query = self.db.query(WorkItemModel).filter(WorkItemModel.site_id == site_id)

        if status:
            query = query.filter(WorkItemModel.status == status)
        if priority:
            query = query.filter(WorkItemModel.priority == priority)
        if assignee_id:
            query = query.filter(WorkItemModel.assignee_id == assignee_id)
        if search:
            query = query.filter(WorkItemModel.title.ilike(f"%{search.strip()}%"))

        if sort_by == "due_date":
            query = query.order_by(WorkItemModel.due_date.asc())
        else:
            query = query.order_by(WorkItemModel.created_at.desc())

        return query.offset(skip).limit(limit).all()

    def update_work_item(
        self, item_id: int, data: WorkItemUpdate, current_user: UserModel
    ) -> WorkItemModel:
        item = self.db.query(WorkItemModel).filter(WorkItemModel.id == item_id).first()
        if not item:
            raise WorkItemNotFoundError() 

        member_info = self._check_site_membership(item.site_id, current_user.id)
        if member_info.role != MemberRole.OWNER and item.assignee_id != current_user.id:
            raise PermissionDeniedError(
                "Chỉ Owner hoặc người được giao việc mới được cập nhật!"
            )

        if data.assignee_id and data.assignee_id != item.assignee_id:
            if member_info.role != MemberRole.OWNER:
                raise PermissionDeniedError(
                    "Chỉ Owner mới có quyền chuyển giao việc cho người khác!"
                )
            self._validate_assignee(item.site_id, data.assignee_id)

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(item, key, value)

        self.db.commit()
        self.db.refresh(item)
        return item

    def get_work_item_detail(
        self, item_id: int, current_user: UserModel
    ) -> WorkItemModel:
        item = self.db.query(WorkItemModel).filter(WorkItemModel.id == item_id).first()
        if not item:
            raise WorkItemNotFoundError()

        self._check_site_membership(item.site_id, current_user.id)
        return item

    def delete_work_item(self, item_id: int, current_user: UserModel) -> None:
        item = self.db.query(WorkItemModel).filter(WorkItemModel.id == item_id).first()
        if not item:
            raise WorkItemNotFoundError()

        member_info = self._check_site_membership(item.site_id, current_user.id)
        if member_info.role != MemberRole.OWNER:
            raise PermissionDeniedError("Chỉ Owner mới có quyền xóa hạng mục thi công!")

        self.db.delete(item)
        self.db.commit()

    def upload_attachment(
        self, item_id: int, file: UploadFile, current_user: UserModel
    ):
        item = self.db.query(WorkItemModel).filter(WorkItemModel.id == item_id).first()
        if not item:
            raise WorkItemNotFoundError()

        member_info = self._check_site_membership(item.site_id, current_user.id)

        if member_info.role != MemberRole.OWNER and item.assignee_id != current_user.id:
            raise PermissionDeniedError(
                "Chỉ Owner hoặc người được giao việc mới được upload file minh chứng!"
            )

        ALLOWED_TYPES = ["image/jpeg", "image/png", "application/pdf"]
        MAX_SIZE = 5 * 1024 * 1024

        if file.content_type not in ALLOWED_TYPES:
            raise InvalidFileTypeError()  

        if file.size > MAX_SIZE:
            raise FileTooLargeError()  

        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        upload_dir = f"uploads/sites/{item.site_id}/work_items/{item_id}"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = f"{upload_dir}/{unique_filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        attachment = WorkItemAttachmentModel(
            work_item_id=item_id,
            file_path=file_path,
            file_name=file.filename,
            file_type=file.content_type,
        )
        self.db.add(attachment)
        self.db.commit()
        return attachment
