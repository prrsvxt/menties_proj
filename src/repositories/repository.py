from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import hashlib
from uuid import UUID


class Repository:
    def __init__(self, db: AsyncSession):
        self.session = db

    @staticmethod
    def get_lock_key(namespace: str, entity_id: UUID) -> int:
        value = f'{namespace}:{entity_id}'.encode()
        digest = hashlib.sha256(value).digest()
        return int.from_bytes(digest[:8], signed=True)

    async def acquire_advisory_lock(self, key: int) -> None:
        await self.session.execute(
            select(func.pg_advisory_xact_lock(key))
        )
