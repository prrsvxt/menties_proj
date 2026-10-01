from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text

from src.models.base import Base
from src.models.enums.project_status import ProjectStatus
from src.models.project_tag import project_tag


class Project(Base):
    __tablename__ = 'projects'

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(default=ProjectStatus.DRAFT)

    tags: Mapped[list['Tag']] = relationship(secondary=project_tag, back_populates='projects')
