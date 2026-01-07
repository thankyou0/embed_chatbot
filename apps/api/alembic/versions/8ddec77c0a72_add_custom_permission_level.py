"""add_custom_permission_level

Revision ID: 8ddec77c0a72
Revises: 2ce1fa430da8
Create Date: 2026-01-06 17:23:53.407924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ddec77c0a72'
down_revision: Union[str, None] = '2ce1fa430da8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'custom' to PermissionLevel enum
    # We use autocommit_block because ALTER TYPE cannot run inside a transaction
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE permissionlevel ADD VALUE IF NOT EXISTS 'custom'")


def downgrade() -> None:
    # Postgres does not support removing enum values
    pass
