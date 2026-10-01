from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums.project_status import ProjectStatus
from src.schemas.tag import TagResponse


class ProjectCreate(BaseModel):
    name: str = Field(min_length=5, max_length=255)
    slug: str = Field(min_length=5, max_length=150)
    description: str = Field(max_length=500)
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT)
    tag_ids: list[UUID] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=5, max_length=255)
    slug: str | None = Field(default=None, min_length=5, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    status: ProjectStatus | None = None
    tag_ids: list[UUID] | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str
    status: ProjectStatus
    tags: list[TagResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
