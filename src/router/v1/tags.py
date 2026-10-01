from uuid import UUID

from fastapi import APIRouter, status

from src.dependencies.tag_deps import (
    GetTagService,
    TransactionalTagService,
)
from src.schemas.tag import TagCreate, TagResponse, TagUpdate


router = APIRouter(
    prefix='/tags',
    tags=['tags'],
)


@router.get(
    '/{tag_id}',
    response_model=TagResponse,
    status_code=status.HTTP_200_OK,
)
async def get_tag_by_id(
        tag_id: UUID,
        service: GetTagService,
):
    return await service.get_tag_by_id(tag_id)


@router.post(
    '/',
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
        data: TagCreate,
        service: TransactionalTagService,
):
    return await service.create_tag(data)


@router.put(
    '/{tag_id}',
    response_model=TagResponse,
    status_code=status.HTTP_200_OK,
)
async def update_tag(
        tag_id: UUID,
        data: TagUpdate,
        service: TransactionalTagService,
):
    return await service.update_tag(tag_id, data)


@router.delete(
    '/{tag_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tag(
        tag_id: UUID,
        service: TransactionalTagService,
):
    await service.delete_tag(tag_id)
