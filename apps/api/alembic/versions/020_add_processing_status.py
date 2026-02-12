"""add_processing_to_ks_status

Revision ID: 020_add_processing_status
Revises: 019_add_ks_error_msg
Create Date: 2026-01-29 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '020_add_processing_status'
down_revision: Union[str, Sequence[str], None] = '019_add_ks_error_msg'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add 'processing' to knowledgesourcestatus enum
    op.execute("ALTER TYPE knowledgesourcestatus ADD VALUE IF NOT EXISTS 'processing'")

def downgrade() -> None:
    # Postgres doesn't easily support removing enum values
    pass
