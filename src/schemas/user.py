from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from uuid import UUID

from src.models.enums.user_enums import UserRole

class BaseUser(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr | None = Field(min_length=5)

class UserSchema(BaseUser):
    id: UUID
    created_at: datetime
    user_role: UserRole
    updated_at: datetime | None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )

class UserCreate(BaseUser): ...

class UserUpdate(BaseUser):
    user_role: UserRole | None = Field(default=UserRole.USER)

class UserResponse(BaseUser):
    id: UUID
    user_role: UserRole
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)