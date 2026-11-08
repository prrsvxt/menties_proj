from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timezone

from src.models.users import UserModel
from src.repositories.repository import Repository

class UserRepository(Repository):
    LOCK_NAMESPACE = 'user'

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_user_by_id(self, user_id: UUID) -> UserModel | None:
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.access_granted))
            .where(
                UserModel.id == user_id,
                UserModel.deleted_at.is_(None),
            )
        )   
        result = await self.session.execute(stmt)
        result = result.scalar_one_or_none()
        return result

    async def get_user_for_update(self, user_id: UUID) -> UserModel | None:
        lock_id = self.get_lock_key(self.LOCK_NAMESPACE, user_id)
        await self.acquire_advisory_lock(lock_id)

        user = await self.get_user_by_id(user_id)
        return user
    
    async def create_user(self, user: UserModel) -> UserModel:
        self.session.add(user)
        await self.session.flush()

        return user
        
    async def delete_user(self, user: UserModel) -> None:
        deleted_at = datetime.now(timezone.utc)
        user.deleted_at = deleted_at

        for access in user.access_granted:
            access.revoke(deleted_at)
            access.deleted_at = deleted_at
        
        await self.session.flush()

    async def update_user(self, user: UserModel) -> UserModel:
        await self.session.flush()

        return user
