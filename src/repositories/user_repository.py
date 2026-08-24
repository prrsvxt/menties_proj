from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from src.models.users import UserModel
from src.schemas.user import UserCreate, UserUpdate
from src.security.passwords import hash_password

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.session = db

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
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
        result = await self.session.scalar(stmt)
        return result

    async def create_user(self, data: UserCreate) -> UserModel:
    
        hashed_password = hash_password(data.password)

        user = UserModel(
            username=data.username,
            email=data.email,
            hashed_password=hashed_password
        )

        try:
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)
        except IntegrityError:
            raise ValueError('Username or email already exists')

        return user

    async def delete_user(self, user_id: int) -> None:

        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_deleted.is_(False)
        )

        existing_user = await self.session.scalar(stmt)
        if not existing_user:
            raise ValueError('User doesn\'t exist')

        existing_user.is_deleted = True

        await self.session.flush()
        await self.session.refresh(existing_user)

    async def update_user(self, user_id: int, data: UserUpdate) -> UserModel:
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_deleted.is_(False)
        )

        user = await self.session.scalar(stmt)

        if user is None:
            raise ValueError('User doesn\'t exist')

        update_data = data.model_dump(exclude_unset=True)

        password = update_data.pop('password', None)

        if password is not None:
            user.hashed_password = hash_password(password)

        for field, value in update_data.items():
            setattr(user, field, value)

        try:

            await self.session.flush()
            await self.session.refresh(user)
        except IntegrityError:
            raise ValueError('Username or email already exists')

        return user