from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update
from uuid import UUID
from datetime import datetime, timezone

from src.models.users import UserModel
from src.models.access_grant import AccessGrant
from src.models.enums.access import AccessStatus

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.session = db

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
    
    async def create_user(self, user: UserModel) -> UserModel:
        self.session.add(user)
        await self.session.flush()

        return user
        
    async def delete_user(self, user: UserModel) -> None:
        deleted_at = datetime.now(timezone.utc)
        user.deleted_at = deleted_at

        for access in user.access_granted:
            access.revoke(deleted_at)
            access_deleted_at = deleted_at
        
        await self.session.flush()

    async def update_user(self, user: UserModel) -> UserModel:
        await self.session.flush()

        return user
