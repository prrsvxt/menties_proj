from fastapi import APIRouter, status
from uuid import UUID

from src.dependencies.users_deps import GetUserService, TransactionalUserService
from src.schemas.user import UserResponse, UserCreate, UserUpdate


router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: UUID,
    service: GetUserService
):
    return await service.get_user_by_id(user_id=user_id)

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: TransactionalUserService
):
    return await service.create_user(data=data)

@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    service: TransactionalUserService
):
    await service.delete_user(user_id=user_id)

@router.put('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: TransactionalUserService
):
    return await service.update_user(
        user_id=user_id,
        data=data
    )

