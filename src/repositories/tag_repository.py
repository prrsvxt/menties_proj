from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from uuid import UUID

from src.repositories.repository import Repository
from src.models.tag import Tag


class TagRepository(Repository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_tag_by_id(self, tag_id: UUID) -> Tag | None:
        # здесь я не использую selectinload, потому что в TagResponse не добавляем вообще Projects,
        # т.к. в таком случае могут быть слишком тяжёлые ответы. 
        # надо будет - добавлю отдельную схему, и отдельный запрос.
        stmt = select(Tag).where(Tag.id == tag_id, Tag.deleted_at.is_(None))
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        return result

    async def get_tags_by_ids(self, tag_ids: list[UUID]) -> list[Tag]:
        stmt = select(Tag).where(Tag.id.in_(tag_ids), Tag.deleted_at.is_(None))
        result = (await self.session.execute(stmt)).scalars().all()
        return result

    async def create_tag(self, tag: Tag) -> Tag:
        self.session.add(tag)
        await self.session.flush()
        return tag

    async def update_tag(self, tag: Tag) -> Tag:
        await self.session.flush()
        return tag

    async def delete_tag(self, tag: Tag) -> None:
        deleted_at = datetime.now(timezone.utc)
        tag.deleted_at = deleted_at

        await self.session.flush()