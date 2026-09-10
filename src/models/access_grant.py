from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, DateTime, func, ForeignKey, ARRAY, Enum
from uuid import uuid4, UUID
from datetime import datetime

from src.models.base import Base
from src.models.enums.access import AccessTypes, AccessStatus


class AccessGrant(Base):
    __tablename__ = "access_grant"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    resource: Mapped[str] = mapped_column(String(50))
    scope: Mapped[list[AccessTypes]] = mapped_column(
            ARRAY(Enum(AccessTypes, name='accesstype')),
            nullable=False,
            default=lambda: [AccessTypes.ACCESS],
        )
    status: Mapped[AccessStatus] = mapped_column(default=AccessStatus.ACTIVE)

    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),)
    expires_at: Mapped[datetime| None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped['UserModel'] = relationship(back_populates='access_granted')