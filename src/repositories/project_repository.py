from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy import select
from datetime import datetime, timezone
from uuid import UUID

from src.repositories.repository import Repository
from src.models.project import Project
from src.models.tag import Tag


class ProjectRepository(Repository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_project_by_id(self, project_id: UUID) -> Project | None:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.tags),
                with_loader_criteria(Tag, Tag.deleted_at.is_(None))
            )
            .where(Project.id == project_id, Project.deleted_at.is_(None))
        )
        result = (await self.session.execute(stmt)).scalar_one_or_none()

        return result

    async def get_paginated_projects(
            self,
            limit: int,
            offset: int
    ) -> list[Project]:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.tags),
                with_loader_criteria(Tag, Tag.deleted_at.is_(None))
            )
            .where(
                Project.deleted_at.is_(None)
            )
            .order_by(
                Project.created_at
            )
            .limit(limit)
            .offset(offset)
        )

        result = (await self.session.execute(stmt)).scalars().all()
        return result

    async def create_project(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project

    async def update_project(self, project: Project) -> Project:
        await self.session.flush()
        return project

    async def delete_project(self, project: Project) -> None:
        deleted_at = datetime.now(timezone.utc)
        project.deleted_at = deleted_at

        await self.session.flush()
