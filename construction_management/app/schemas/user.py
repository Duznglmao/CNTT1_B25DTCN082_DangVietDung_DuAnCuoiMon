from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import RoleUser


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if " " in v:
            raise ValueError("Mật khẩu không được chứa khoảng trắng!")
        if not any(char.isupper() for char in v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ hoa!")
        if not any(char.islower() for char in v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ thường!")
        if not any(char.isdigit() for char in v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ số!")
        return v


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    is_active: bool | None = None


class UserResponse(UserBase):
    id: int
    role: RoleUser
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAdminResponse(UserResponse):
    pass
