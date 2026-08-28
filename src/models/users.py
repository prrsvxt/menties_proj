import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

from src.models.enums.user_enums import UserRole

metadata = sa.MetaData()


class BaseServiceModel:
    """Базовый класс для таблиц сервиса."""

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None


Base: DeclarativeMeta = declarative_base(metadata=metadata, cls=BaseServiceModel)

class UserModel(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(sa.String())
    email: Mapped[str | None] = mapped_column(sa.String())
    user_role: Mapped[UserRole] = mapped_column(sa.Enum(UserRole), default=UserRole.USER)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(), server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(), 
        onupdate=sa.func.now(),
        nullable=True
    )

    is_deleted: Mapped[bool] = mapped_column(sa.Boolean(), default=False)
    
