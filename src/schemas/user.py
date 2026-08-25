from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID

from src.enums.user_enums import UserRole

class BaseUser(BaseModel):
    username: str
    email: EmailStr | None

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
    user_role: UserRole | None 

class UserResponse(BaseUser):
    id: UUID
    user_role: UserRole
    created_at: datetime
    updated_at: datetime | None