from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import hashlib
from uuid import UUID
from base64 import urlsafe_b64encode, urlsafe_b64decode
import json
from datetime import datetime


class Repository:
    def __init__(self, db: AsyncSession):
        self.session = db

    @staticmethod
    def get_lock_key(namespace: str, entity_id: UUID) -> int:
        value = f'{namespace}:{entity_id}'.encode()
        digest = hashlib.sha256(value).digest()
        return int.from_bytes(digest[:8])

    async def acquire_advisory_lock(self, key: int) -> None:
        await self.session.execute(
            select(func.pg_advisory_xact_lock(key))
        )

    def cursor_decode(self, cursor: str) -> tuple[UUID, datetime]:
        
        cursor_decoded = json.loads(urlsafe_b64decode(cursor).decode())

        cursor_id = UUID(cursor_decoded['id'])
        cursor_timestamp = datetime.fromisoformat(cursor_decoded['created_at'])

        return cursor_id, cursor_timestamp

    def cursor_encode(self, obj) -> str:

        cursor_data = {
            'id': str(obj.id),
            'created_at': obj.created_at.isoformat()
        }

        cursor_json = json.dumps(cursor_data, separators=(',', ':'))
        cursor_encoded = urlsafe_b64encode(cursor_json.encode()).decode()

        return cursor_encoded