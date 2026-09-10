from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from uuid import UUID

from src.models.enums.user_enums import UserRole
from src.schemas.access_grant import AccessGrantCreate, AccessGrantResponse

class BaseUser(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr | None = None

class UserSchema(BaseUser):
    id: UUID
    user_role: UserRole
    updated_at: datetime | None
    is_deleted: bool

    model_config = ConfigDict(
        from_attributes=True,
    )

class UserCreate(BaseUser):
    access_granted: list[AccessGrantCreate] = Field(default_factory=list)

class UserUpdate(BaseUser):
    username: str | None = None
    email: EmailStr | None = None
    user_role: UserRole | None = Field(default=UserRole.USER)
    access_granted_to_add: list[AccessGrantCreate] | None = None

class UserResponse(BaseUser):
    id: UUID
    user_role: UserRole
    updated_at: datetime | None
    access_granted: list[AccessGrantResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)