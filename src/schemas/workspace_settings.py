from pydantic import BaseModel, ConfigDict, Field, field_validator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class WorkspaceSettingsCreate(BaseModel):
    timezone: str = Field(default='UTC')
    language: str = Field(min_length=2, max_length=30)
    notifications_enabled: bool = True

    @field_validator('timezone')
    @classmethod
    def timezone_validate(cls, value: str) -> str:
        try: 
            ZoneInfo(value)
        except ZoneInfoNotFoundError:
            raise ValueError('Некорректный часовой пояс')
        return value


class WorkspaceSettingsUpdate(BaseModel):
    timezone: str | None = Field(default=None)
    language: str | None = Field(default=None, min_length=2, max_length=30)
    notifications_enabled: bool | None = None

    @field_validator('timezone')
    @classmethod
    def timezone_validate(cls, value: str | None) -> str | None:
        if value is None:
            return value

        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError:
            raise ValueError('Некорректный часовой пояс')
        return value


class WorkspaceSettingsResponse(BaseModel):
    timezone: str
    language: str
    notifications_enabled: bool

    model_config = ConfigDict(from_attributes=True)
