from datetime import datetime
import enum
from sqlalchemy import String, func, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db import Base


class WorkItemStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class WorkItemPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class WorkItemModel(Base):
    __tablename__ = "work_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("construction_sites.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[WorkItemStatus] = mapped_column(default=WorkItemStatus.TODO)
    priority: Mapped[WorkItemPriority] = mapped_column(
        default=WorkItemPriority.MEDIUM,
    )
    due_date: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    site: Mapped["ConstructionSiteModel"] = relationship(
        "ConstructionSiteModel", back_populates="work_items"
    )
    assignee: Mapped["UserModel | None"] = relationship(
        "UserModel", back_populates="work_items"
    )
