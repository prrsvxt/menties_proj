from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.models.users import UserModel


class UserMapper:

    def user_create_map(self, data: UserCreate) -> UserModel:
        return UserModel(**data.model_dump())

    def user_update_map(self, data: UserUpdate, user: UserModel) -> UserModel:
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        return user
 
    def user_response_map(self, data: UserModel) -> UserResponse:
        return UserResponse.model_validate(data)