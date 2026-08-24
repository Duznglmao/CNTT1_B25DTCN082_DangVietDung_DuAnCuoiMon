from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.site import MemberRole
from app.schemas.user import UserResponse


class ConstructionSiteBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class ConstructionSiteCreate(ConstructionSiteBase):
    pass


class ConstructionSiteUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class ConstructionSiteResponse(ConstructionSiteBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SiteMemberCreate(BaseModel):
    user_id: int
    role: MemberRole = MemberRole.MEMBER


class SiteMemberResponse(BaseModel):
    site_id: int
    user_id: int
    role: MemberRole
    joined_at: datetime
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)
