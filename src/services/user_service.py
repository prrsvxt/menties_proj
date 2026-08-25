from uuid import UUID

from src.repositories.user_repository import UserRepository
from src.mappers.user_mapper import UserMapper
from src.schemas.user import UserCreate, UserUpdate
from src.models.users import UserModel
from src.errors.user_errors import UserNotFoundError, UserAlreadyExistsError


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user_by_id(self, user_id: UUID) -> UserModel:
        user = await self.repository.get_user_by_id(user_id)

        if user is None:
            raise UserNotFoundError('User not found')

        return user

    async def get_user_by_username(self, username: str) -> UserModel:
        user = await self.repository.get_user_by_username(username)
    
        if user is None:
            raise UserNotFoundError('User not found')
    
        return user

    async def create_user(self, data: UserCreate) -> UserModel:
        exitsting_user = await self.repository.get_user_by_username(data.username)

        if exitsting_user is not None:
            raise UserAlreadyExistsError('User Already Exists')
        
        user_data = UserMapper.user_create_map(data)
        return await self.repository.create_user(user_data)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserModel:
        user = await self.get_user_by_id(user_id=user_id)
        user = UserMapper.user_update_map(data, user)

        return await self.repository.update_user(user)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.get_user_by_id(user_id)
        await self.repository.delete_user(user)

    