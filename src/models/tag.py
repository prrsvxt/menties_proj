from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.project_tag import project_tag


class Tag(Base):
    __tablename__ = 'tags'

    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text)
    color: Mapped[str] = mapped_column(String(7))

    projects: Mapped[list['Project']] = relationship(secondary=project_tag, back_populates='tags')
