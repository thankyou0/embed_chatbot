"""add content_hash to uploaded_files

Revision ID: f21b34c56d78
Revises: 96f9c273fa63, e1c9b8c7d6a5
Create Date: 2026-01-29 16:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f21b34c56d78'
down_revision: Union[str, tuple, None] = ('96f9c273fa63', 'e1c9b8c7d6a5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add content_hash column to uploaded_files
    op.add_column('uploaded_files', sa.Column('content_hash', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_uploaded_files_content_hash'), 'uploaded_files', ['content_hash'], unique=False)
    
    # Add content_hash column to crawled_pages
    op.add_column('crawled_pages', sa.Column('content_hash', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_crawled_pages_content_hash'), 'crawled_pages', ['content_hash'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_crawled_pages_content_hash'), table_name='crawled_pages')
    op.drop_column('crawled_pages', 'content_hash')
    op.drop_index(op.f('ix_uploaded_files_content_hash'), table_name='uploaded_files')
    op.drop_column('uploaded_files', 'content_hash')
