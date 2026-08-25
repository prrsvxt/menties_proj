from fastapi import APIRouter, status, HTTPException
from uuid import UUID

from src.dependencies.users_deps import GetUserService
from src.schemas.user import UserResponse, UserCreate, UserUpdate
from src.errors.user_errors import UserAlreadyExistsError, UserNotFoundError


router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.get('/{user_id:uuid}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: UUID,
    service: GetUserService
):
    try:
        return await service.get_user_by_id(user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found')

@router.get('/{username}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_username(
    username: str,
    service: GetUserService
):
    try:
        return await service.get_user_by_username(username=username)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found')

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: GetUserService
):
    try:
        return await service.create_user(data=data)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    service: GetUserService
):
    try:
        await service.delete_user(user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found')

@router.put('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: GetUserService
):
    try:
        return await service.update_user(
            user_id=user_id,
            data=data
        )
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

