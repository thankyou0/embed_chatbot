"""Add error_message to knowledge_sources

Revision ID: 019_add_ks_error_msg
Revises: 018_add_product_metadata, 017_add_password_reset_tokens
Create Date: 2026-01-19 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '019_add_ks_error_msg'
down_revision: Union[str, Sequence[str]] = ('018_add_product_metadata', '017_add_password_reset_tokens')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add error_message column to knowledge_sources table
    op.add_column('knowledge_sources', sa.Column('error_message', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('knowledge_sources', 'error_message')
