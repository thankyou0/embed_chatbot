"""add is_preview to chat_session

Revision ID: 016_add_is_preview_session
Revises: 015_add_username_to_user
Create Date: 2026-01-09 16:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '016_add_is_preview_session'
down_revision: Union[str, None] = '015_add_username_to_user'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chat_sessions', sa.Column('is_preview', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('chat_sessions', 'is_preview')
