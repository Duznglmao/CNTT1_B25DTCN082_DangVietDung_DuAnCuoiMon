from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.work_item import WorkItemPriority, WorkItemStatus


class AttachmentResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WorkItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: WorkItemPriority = WorkItemPriority.MEDIUM
    assignee_id: int | None = Field(None, gt=0)


    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: datetime | None) -> datetime | None:
        if v and v < datetime.now(timezone.utc):
            raise ValueError("Hạn chót không được nằm trong quá khứ!")
        return v


class WorkItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: WorkItemPriority | None = None
    status: WorkItemStatus | None = None
    assignee_id: int | None = None


class WorkItemResponse(WorkItemCreate):
    id: int
    site_id: int
    status: WorkItemStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WorkItemDetailResponse(WorkItemResponse):
    attachments: list[AttachmentResponse] = []
