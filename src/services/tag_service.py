from uuid import UUID

from src.repositories.tag_repository import TagRepository
from src.schemas.tag import TagCreate, TagResponse, TagUpdate
from src.models.tag import Tag
from src.exceptions.general_errors import NotFoundError
from src.mappers.tag_mapper import TagMapper


class TagService:
    def __init__(
            self, 
            repository: TagRepository,
            mapper: TagMapper
    ):
        self.repository = repository
        self.mapper = mapper

    async def _get_tag_by_id(self, tag_id: UUID) -> Tag:
        tag = await self.repository.get_tag_by_id(tag_id)

        if tag is None:
            raise NotFoundError(f'Tag with id={tag_id} not found.')

        return tag

    async def get_tag_by_id(self, tag_id: UUID) -> TagResponse:
        tag = await self._get_tag_by_id(tag_id)
        return self.mapper.tag_response_map(tag)

    async def create_tag(
            self,
            data: TagCreate
    ) -> TagResponse:
        tag = self.mapper.tag_create_map(data)
        tag = await self.repository.create_tag(tag)
        tag = self.mapper.tag_response_map(tag)
        return tag

    async def update_tag(
            self,
            tag_id: UUID,
            data: TagUpdate,
    ) -> TagResponse:
        tag = await self._get_tag_by_id(tag_id)
        tag_update = self.mapper.tag_update_map(data, tag)
        tag = await self.repository.update_tag(tag_update)
        tag = self.mapper.tag_response_map(tag)
        return tag

    async def delete_tag(
            self,
            tag_id: UUID
    ) -> None:
        tag = await self._get_tag_by_id(tag_id)
        await self.repository.delete_tag(tag)