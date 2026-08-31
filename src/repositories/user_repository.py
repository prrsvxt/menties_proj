from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from uuid import UUID
import logging
from functools import wraps

from src.models.users import UserModel


logger = logging.getLogger(__name__)

def log_sqlalchemy_error(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError:
            logger.exception('Database operation failed in %s', func.__name__)
            raise

    return wrapper

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.session = db

    @log_sqlalchemy_error
    async def get_user_by_id(self, user_id: UUID) -> UserModel | None:
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_deleted == False
        )
        result = await self.session.execute(stmt)
        result = result.scalar_one_or_none()
        return result

    @log_sqlalchemy_error
    async def create_user(self, user: UserModel) -> UserModel:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user
        
    @log_sqlalchemy_error
    async def delete_user(self, user: UserModel) -> None:
        user.is_deleted = True
        
        await self.session.flush()
        await self.session.refresh(user)

    @log_sqlalchemy_error
    async def update_user(self, user: UserModel) -> UserModel:
        await self.session.flush()
        await self.session.refresh(user)

        return user
