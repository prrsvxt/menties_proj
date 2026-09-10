from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.models.users import UserModel
from src.models.access_grant import AccessGrant


class UserMapper:

    def user_create_map(self, data: UserCreate) -> UserModel:
        return UserModel(
            **data.model_dump(exclude={'access_granted'}),
            access_granted=[
                AccessGrant(**grant.model_dump())
                for grant in data.access_granted
            ]
        )

    def user_update_map(self, data: UserUpdate, user: UserModel) -> UserModel:
        update_data = data.model_dump(
            exclude_unset=True,
            exclude={'access_granted_to_add'},
        )

        if data.access_granted_to_add is not None:
            user.access_granted.extend(
                AccessGrant(**access.model_dump())
                for access in data.access_granted_to_add
            )
        
        for field, value in update_data.items():
            setattr(user, field, value)
        return user
 
    def user_response_map(self, data: UserModel) -> UserResponse:
        return UserResponse.model_validate(data)