"""Add analytics fields

Revision ID: 011_analytics
Revises: 010_add_chat_history
Create Date: 2026-01-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '011_analytics'
down_revision: Union[str, None] = '010_add_chat_history'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add confidence_threshold to chatbots table
    op.add_column('chatbots', sa.Column('confidence_threshold', sa.Float(), nullable=False, server_default='0.7'))


def downgrade() -> None:
    op.drop_column('chatbots', 'confidence_threshold')

