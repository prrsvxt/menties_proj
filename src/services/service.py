import json 
from uuid import UUID
from datetime import datetime
from base64 import urlsafe_b64decode, urlsafe_b64encode

from src.cache.redis_cache import RedisCache

class Service:

    def __init__(self, redis: RedisCache):
        self.redis = redis

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