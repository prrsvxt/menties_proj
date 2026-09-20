import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.enums.user_enums import UserRole
from src.models.base import Base

class UserModel(Base):
    __tablename__ = 'users'
    username: Mapped[str] = mapped_column(sa.String())
    email: Mapped[str | None] = mapped_column(sa.String())
    user_role: Mapped[UserRole] = mapped_column(sa.Enum(UserRole), default=UserRole.USER)
    
    access_granted: Mapped[list['AccessGrant']] = relationship(back_populates='user')
