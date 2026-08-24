from datetime import datetime
import enum
from sqlalchemy import String, Enum, func, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db import Base


class RoleUser(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[RoleUser] = mapped_column(default=RoleUser.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    owned_sites: Mapped[list["ConstructionSiteModel"]] = relationship(
        "ConstructionSiteModel", back_populates="owner"
    )
    site_members: Mapped[list["SiteMemberModel"]] = relationship(
        "SiteMemberModel", back_populates="user"
    )
    work_items: Mapped[list["WorkItemModel"]] = relationship(
        "WorkItemModel", back_populates="assignee"
    )
