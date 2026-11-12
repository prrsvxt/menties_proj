from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_ 
from sqlalchemy.orm import selectinload

from uuid import UUID
from datetime import timezone, datetime

from src.models.workspace import WorkspaceModel
from src.repositories.repository import Repository

class WorkspaceRepository(Repository):
    LOCK_NAMESPACE = 'workspace'

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_workspace_by_id(self, workspace_id: UUID) -> WorkspaceModel | None:
        stmt = (
            select(WorkspaceModel)
                .options(selectinload(WorkspaceModel.workspace_settings))
                .where(
                WorkspaceModel.id == workspace_id,
                WorkspaceModel.deleted_at.is_(None)
            )
        )
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        return result

    async def get_workspace_with_lock(
            self,
            workspace_id: UUID,
    ) -> WorkspaceModel | None:
        lock_id = self.get_lock_key(self.LOCK_NAMESPACE, workspace_id)
        await self.acquire_advisory_lock(lock_id)

        workspace = await self.get_workspace_by_id(workspace_id)
        return workspace

    async def get_paginated_workspaces(
            self,
            limit: int,
            cursor_workspace_id: UUID | None,
            cursor_timestamp: datetime | None,
    ) -> list[WorkspaceModel]:

        conditions = [
            WorkspaceModel.deleted_at.is_(None),
        ]

        if cursor_workspace_id and cursor_timestamp:
            conditions.append(
                or_(
                    WorkspaceModel.created_at > cursor_timestamp,
                    and_(
                        WorkspaceModel.created_at == cursor_timestamp,
                        WorkspaceModel.id > cursor_workspace_id
                    )
                )
            )
        
        stmt = (
            select(WorkspaceModel)
            .options(selectinload(WorkspaceModel.workspace_settings))
            .where(*conditions)
            .order_by(WorkspaceModel.created_at, WorkspaceModel.id)
            .limit(limit + 1)
        )
        result = (await self.session.execute(stmt)).scalars().all()

        return result

    async def create_workspace(
            self, 
            workspace: WorkspaceModel
    ) -> WorkspaceModel:
        self.session.add(workspace)
        await self.session.flush()

        return workspace

    async def delete_workspace(
            self, 
            workspace: WorkspaceModel
    ) -> None:
        deleted_at = datetime.now(timezone.utc)
        workspace.deleted_at = deleted_at
        workspace.workspace_settings.deleted_at = deleted_at

        await self.session.flush()

    async def update_workspace(
            self,
            workspace: WorkspaceModel
    ) -> WorkspaceModel:
        self.session.add(workspace)
        await self.session.flush()

        return workspace
