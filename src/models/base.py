import sqlalchemy as sa
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column

metadata = sa.MetaData()

class CommonFieldsMixin:
    id: Mapped[UUID] = mapped_column(
        sa.Uuid(),
        primary_key=True,
        default=uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        onupdate=sa.func.now(),
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )


class BaseServiceModel(CommonFieldsMixin):
    """Базовый класс для таблиц сервиса."""

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None

    


Base: DeclarativeMeta = declarative_base(metadata=metadata, cls=BaseServiceModel)
