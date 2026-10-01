from pydantic import BaseModel, ConfigDict, Field

from src.models.enums.workspace_status import WorkspaceStatus
from src.schemas.workspace_settings import (
    WorkspaceSettingsCreate,
    WorkspaceSettingsResponse,
    WorkspaceSettingsUpdate,
)


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=5)
    slug: str = Field(min_length=5)
    description: str = Field(max_length=500)
    status: WorkspaceStatus = Field(default=WorkspaceStatus.ACTIVE)
    workspace_settings: WorkspaceSettingsCreate


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=5)
    slug: str | None = Field(default=None, min_length=5)
    description: str | None = Field(default=None, max_length=500)
    status: WorkspaceStatus | None = None
    workspace_settings: WorkspaceSettingsUpdate | None = None

class WorkspaceResponse(BaseModel):
    name: str
    slug: str
    description: str
    status: WorkspaceStatus
    workspace_settings: WorkspaceSettingsResponse

    model_config = ConfigDict(from_attributes=True)
