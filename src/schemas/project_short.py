from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models.enums.project_status import ProjectStatus


class ProjectShortResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str
    status: ProjectStatus

    model_config = ConfigDict(from_attributes=True)
