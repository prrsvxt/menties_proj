from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100)
    description: str = Field(max_length=300)
    color: str = Field(min_length=4, max_length=7)


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    slug: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    color: str | None = Field(default=None, min_length=4, max_length=7)


class TagResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str
    color: str

    model_config = ConfigDict(from_attributes=True)
