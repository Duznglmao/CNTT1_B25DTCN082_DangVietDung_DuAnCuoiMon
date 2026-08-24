from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class ActivityLogModel(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("construction_sites.id", ondelete="SET NULL"), index=True
    )
    action: Mapped[str] = mapped_column(String(50))
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["UserModel | None"] = relationship("UserModel")
    site: Mapped["ConstructionSiteModel | None"] = relationship("ConstructionSiteModel")
