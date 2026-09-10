import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import UUID, uuid4

from src.models.enums.user_enums import UserRole
from src.models.base import Base

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
    
    access_granted: Mapped[list['AccessGrant']] = relationship(back_populates='user')