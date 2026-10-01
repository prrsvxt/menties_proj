from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey
from uuid import UUID

from src.models.base import Base


class WorkspaceSettingsModel(Base):
    __tablename__ = 'workspace_settings'

    timezone: Mapped[str] = mapped_column(String(50), default='UTC')
    language: Mapped[str] = mapped_column(String(30))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey('workspaces.id'), unique=True)

    workspace: Mapped['WorkspaceModel'] = relationship(back_populates='workspace_settings')