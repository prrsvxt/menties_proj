from src.schemas.user import UserCreate, UserUpdate
from src.models.users import UserModel


class UserMapper:

    @staticmethod
    def user_create_map(data: UserCreate) -> UserModel:
        return UserModel(**data.model_dump())

    @staticmethod
    def user_update_map(data: UserUpdate, user: UserModel) -> UserModel:
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        return user