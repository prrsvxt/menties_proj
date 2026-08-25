from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.models.users import UserModel

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.session = db

    async def get_user_by_id(self, user_id: UUID) -> UserModel | None:
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_deleted == False
        )
        result = await self.session.scalar(stmt)
        return result

    async def get_user_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserModel).where(
            UserModel.username == username,
            UserModel.is_deleted == False
        )
        result = await self.session.execute(stmt)
        result = result.scalar_one_or_none()
        return result

    async def create_user(self, user: UserModel) -> UserModel:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user
        

    async def delete_user(self, user: UserModel) -> None:
        user.is_deleted = True
        
        await self.session.flush()
        await self.session.refresh(user)

    async def update_user(self, user: UserModel) -> UserModel:
        await self.session.flush()
        await self.session.refresh(user)

        return user