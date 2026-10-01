from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import timezone, datetime

from src.models.workspace import WorkspaceModel

class WorkspaceRepository:
    def __init__(self, db: AsyncSession):
        self.session = db

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

    async def get_paginated_workspaces(
            self,
            limit: int,
            offset: int,
    ) -> list[WorkspaceModel]:
        stmt = (
            select(WorkspaceModel)
            .options(selectinload(WorkspaceModel.workspace_settings))
            .where(WorkspaceModel.deleted_at.is_(None))
            .order_by(WorkspaceModel.created_at, WorkspaceModel.id)
            .limit(limit)
            .offset(offset)
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
        await self.session.flush()

        return workspace
