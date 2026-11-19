from sqlalchemy import ForeignKey, Table, Column, Uuid

from src.models.base import Base

project_tag = Table(
    'project_tag',
    Base.metadata,
    Column('project_id', Uuid, ForeignKey('projects.id'), primary_key=True),
    Column('tag_id', Uuid, ForeignKey('tags.id'), primary_key=True)
)