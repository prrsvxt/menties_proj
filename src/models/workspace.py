from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text

from src.models.base import Base
from src.models.enums.workspace_status import WorkspaceStatus


class WorkspaceModel(Base):
    __tablename__ = 'workspaces'

    name: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[WorkspaceStatus] = mapped_column(default=WorkspaceStatus.ACTIVE)

    workspace_settings: Mapped['WorkspaceSettingsModel'] = relationship(back_populates='workspace')