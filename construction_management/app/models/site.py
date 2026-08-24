from datetime import datetime
import enum
from sqlalchemy import String, func, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db import Base


class MemberRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class ConstructionSiteModel(Base):
    __tablename__ = "construction_sites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)

    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="owned_sites")
    members: Mapped[list["SiteMemberModel"]] = relationship(
        "SiteMemberModel", back_populates="site"
    )
    work_items: Mapped[list["WorkItemModel"]] = relationship(
        "WorkItemModel", back_populates="site"
    )


class SiteMemberModel(Base):
    __tablename__ = "site_members"

    site_id: Mapped[int] = mapped_column(
        ForeignKey("construction_sites.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role: Mapped[MemberRole] = mapped_column(default=MemberRole.MEMBER)
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

    site: Mapped["ConstructionSiteModel"] = relationship(
        "ConstructionSiteModel", back_populates="members"
    )
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="site_members")
