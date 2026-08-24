from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.work_item import WorkItemPriority, WorkItemStatus


class WorkItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: WorkItemPriority = WorkItemPriority.MEDIUM


class WorkItemCreate(WorkItemBase):
    assignee_id: int | None = None


class WorkItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    assignee_id: int | None = None
    status: WorkItemStatus | None = None
    priority: WorkItemPriority | None = None
    due_date: datetime | None = None


class WorkItemResponse(WorkItemBase):
    id: int
    site_id: int
    assignee_id: int | None
    status: WorkItemStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
