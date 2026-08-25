"""Expanded User Model

Revision ID: a6cf1d6dd1de
Revises: 0e3f256d364c
Create Date: 2026-08-25 15:09:48.262723
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6cf1d6dd1de'
down_revision: Union[str, Sequence[str], None] = '0e3f256d364c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    user_role_enum = sa.Enum(
        'ADMIN',
        'USER',
        'MODERATOR',
        name='userrole'
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('user_role', user_role_enum, nullable=False, server_default='USER'))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), server_default=sa.false(), nullable=False))

    op.alter_column('users', 'user_role', server_default=None)
    op.alter_column('users', 'is_deleted', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'user_role')
    op.drop_column('users', 'email')

    user_role_enum = sa.Enum(
        'ADMIN',
        'USER',
        'MODERATOR',
        name='userrole'
    )
    user_role_enum.drop(op.get_bind(), checkfirst=True)