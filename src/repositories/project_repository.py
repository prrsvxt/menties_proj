from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy import select, or_, and_

from datetime import datetime, timezone
from uuid import UUID

from src.repositories.repository import Repository
from src.exceptions.general_errors import ConflictError
from src.models.project import Project
from src.models.project_tag import project_tag
from src.models.tag import Tag


class ProjectRepository(Repository):
    LOCK_NAMESPACE = 'project'

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

    async def get_project_with_lock(self, project_id: UUID) -> Project | None:
        lock_id = self.get_lock_key(self.LOCK_NAMESPACE, project_id)
        await self.acquire_advisory_lock(lock_id)

        project = await self.get_project_by_id(project_id)
        return project

    async def get_paginated_projects(
            self,
            limit: int,
            cursor_project_id: UUID | None,
            cursor_timestamp: datetime | None
    ) -> list[Project]:

        conditions = [
            Project.deleted_at.is_(None),
        ]

        if cursor_project_id and cursor_timestamp:

            conditions.append(
                or_(
                    Project.created_at > cursor_timestamp,
                    and_(
                        Project.created_at == cursor_timestamp,
                        Project.id > cursor_project_id,
                    )
                )
            )

        stmt = (
            select(Project)
            .options(
                selectinload(Project.tags),
                with_loader_criteria(Tag, Tag.deleted_at.is_(None)),
            )
            .where(*conditions)
            .order_by(
                Project.created_at,
                Project.id,
            )
            .limit(limit + 1)
        )

        result = (await self.session.execute(stmt)).scalars().all()

        return result

    async def _get_or_create_tags(self, tags: list[Tag]) -> list[Tag]:

        if not tags:
            return []

        for tag in tags:
            tag_data = {
                column.name: getattr(tag, column.name)
                for column in tag.__table__.columns
                if getattr(tag, column.name) is not None
            }

            create_tag = (
                insert(Tag)
                .values(tag_data)
                .on_conflict_do_nothing()
            )

            await self.session.execute(create_tag)

        tag_slugs = [tag.slug for tag in tags]

        result = await self.session.execute(
            select(Tag).where(
                Tag.slug.in_(tag_slugs),
                Tag.deleted_at.is_(None),
            )
        )
        return result.scalars().all()

    async def create_project(self, project: Project) -> Project:

        values = {
            column.name: getattr(project, column.name)
            for column in project.__table__.columns
            if getattr(project, column.name) is not None
        }

        project_insert = (
            insert(Project)
            .values(values)
            .on_conflict_do_nothing()
            .returning(Project.id)
        )

        project_id = (await self.session.execute(project_insert)).scalar_one_or_none()

        if project_id is None:
            raise ConflictError(f'Project with slug={project.slug} already exists')

        if project.tags:
            persisted_tags = await self._get_or_create_tags(project.tags)

            tag_links = [
                {
                    'project_id': project_id,
                    'tag_id': tag.id
                }
                for tag in persisted_tags
            ]

            tags_insert = (
                insert(project_tag)
                .values(tag_links)
                .on_conflict_do_nothing()
            )

            await self.session.execute(tags_insert)

        await self.session.flush()

        project = await self.get_project_by_id(project_id)
        return project

    async def update_project(
            self,
            project: Project,
            tags: list[Tag] | None,
    ) -> Project:
        if tags is not None:
            project.tags = await self._get_or_create_tags(tags)

        self.session.add(project)
        await self.session.flush()
        return project

    async def delete_project(self, project: Project) -> None:
        deleted_at = datetime.now(timezone.utc)
        project.deleted_at = deleted_at

        await self.session.flush()
