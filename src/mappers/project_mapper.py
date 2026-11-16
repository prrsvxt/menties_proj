from src.schemas.project import (
    ProjectCreate,
    ProjectPaginationResponse,
    ProjectResponse,
    ProjectUpdate,
)
from src.models.project import Project
from src.models.tag import Tag


class ProjectMapper:
    def project_create_map(
            self, 
            data: ProjectCreate,
    ) -> Project:

        tags = [Tag(**tag.model_dump()) for tag in data.tags]
        
        return Project(
            **data.model_dump(exclude={'tags'}),
            tags=tags
        )

    def project_response_map(
            self,
            data: Project,
    ) -> ProjectResponse:
        return ProjectResponse.model_validate(data)

    def project_update_map(
            self,
            data: ProjectUpdate,
            project: Project
    ) -> tuple[Project, list[Tag] | None]:
        update_project = data.model_dump(
            exclude_unset=True,
            exclude={'tags'}
        )

        for field, value in update_project.items():
            setattr(project, field, value)

        tags = None

        if data.tags is not None:
            tags = [Tag(**tag.model_dump()) for tag in data.tags]

        return project, tags

    def multiple_projects_response_map(
            self,
            projects: list[Project]
    ) -> list[ProjectResponse]:
        return [self.project_response_map(project) for project in projects]

    def project_pagination_response_map(
            self,
            projects: list[Project],
            next_cursor: str | None,
    ) -> ProjectPaginationResponse:
        return ProjectPaginationResponse(
            items=self.multiple_projects_response_map(projects),
            next_cursor=next_cursor,
        )
