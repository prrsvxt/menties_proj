from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID

from src.models.enums.access import AccessStatus, AccessTypes


class AccessGrantCreate(BaseModel):
    resource: str = Field(
        min_length=5,
        description="Ресурс, к которому предоставляется доступ",
        examples=["reports"],
    )

    scope: list[AccessTypes] = Field(
        min_length=1,
        description="Разрешённые операции над ресурсом",
        examples=[["access", "export"]],
    )

    status: AccessStatus = Field(
        default=AccessStatus.ACTIVE,
        description="Текущий статус доступа",
    )

    expires_at: datetime | None = Field(
        default=None,
        description="Дата окончания доступа",
    )

class AccessGrantResponse(BaseModel):
    id: UUID
    resource: str
    scope: list[AccessTypes]
    status: AccessStatus
    granted_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)