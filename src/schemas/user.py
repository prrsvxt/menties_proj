from pydantic import BaseModel, EmailStr, SecretStr, ConfigDict
from datetime import datetime


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr | None
    password: SecretStr
    created_at: datetime
    updated_at: datetime
    is_actice: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserCreate(BaseModel):
    username: str
    email: EmailStr | None
    password: str

class UserUpdate(BaseModel):
    username: str | None
    email: EmailStr | None
    password: str | None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr | None
    created_at: datetime
    updated_at: datetime