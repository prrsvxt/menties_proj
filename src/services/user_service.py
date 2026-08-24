from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate
from src.models.users import UserModel


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user_by_id(self, user_id: int) -> UserModel:
        user = await self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError('User doesn\'t exist')

        return user

    async def get_user_by_username(self, username: str) -> UserModel:
        user = await self.repository.get_user_by_username(username)
    
        if user is None:
            raise ValueError('User doesn\'t exist')
    
        return user

    async def create_user(self, data: UserCreate) -> UserModel:
        return await self.repository.create_user(data)

    async def update_user(self, user_id: int, data: UserUpdate) -> UserModel:
        return await self.repository.update_user(user_id, data)

    async def delete_user(self, user_id: int) -> None:
        await self.repository.delete_user(user_id)

    