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
            tags: list[Tag]
    ) -> Project:
        return Project(
            **data.model_dump(exclude={'tag_ids'}),
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
            tags: list[Tag],
            project: Project
    ) -> Project:
        update_project = data.model_dump(
            exclude_unset=True,
            exclude={'tag_ids'}
        )

        for field, value in update_project.items():
            setattr(project, field, value)

        project.tags = tags
        return project

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
