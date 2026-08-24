from fastapi import APIRouter, Depends

from src.dependencies import GetUserService
from src.schemas.user import UserResponse, UserCreate, UserUpdate
from src.services.user_service import UserService


router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.get('/{user_id:int}', response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    service: GetUserService
):
    return await service.get_user_by_id(user_id=user_id)

@router.get('/{username}', response_model=UserResponse)
async def get_user_by_username(
    username: str,
    service: GetUserService
):
    return await service.get_user_by_username(username=username)

@router.post('/', response_model=UserResponse)
async def create_user(
    data: UserCreate,
    service: GetUserService
):
    return await service.create_user(data=data)

@router.delete('/{user_id}')
async def delete_user(
    user_id: int,
    service: GetUserService
):
    await service.delete_user(user_id=user_id)

@router.put('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    service: GetUserService
):
    return await service.update_user(
        user_id=user_id,
        data=data
    )

