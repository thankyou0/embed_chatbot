"""add content_hash to uploaded_files

Revision ID: 021_add_content_hash
Revises: 020_add_processing_status
Create Date: 2026-01-29 16:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '021_add_content_hash'
down_revision: Union[str, None] = '020_add_processing_status'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get connection to check if columns exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Add content_hash column to uploaded_files if it doesn't exist
    uploaded_files_columns = [col['name'] for col in inspector.get_columns('uploaded_files')]
    if 'content_hash' not in uploaded_files_columns:
        op.add_column('uploaded_files', sa.Column('content_hash', sa.String(length=64), nullable=True))
    
    # Add index if it doesn't exist
    uploaded_files_indexes = [idx['name'] for idx in inspector.get_indexes('uploaded_files')]
    if 'ix_uploaded_files_content_hash' not in uploaded_files_indexes:
        op.create_index(op.f('ix_uploaded_files_content_hash'), 'uploaded_files', ['content_hash'], unique=False)
    
    # Add content_hash column to crawled_pages if it doesn't exist
    crawled_pages_columns = [col['name'] for col in inspector.get_columns('crawled_pages')]
    if 'content_hash' not in crawled_pages_columns:
        op.add_column('crawled_pages', sa.Column('content_hash', sa.String(length=64), nullable=True))
    
    # Add index if it doesn't exist
    crawled_pages_indexes = [idx['name'] for idx in inspector.get_indexes('crawled_pages')]
    if 'ix_crawled_pages_content_hash' not in crawled_pages_indexes:
        op.create_index(op.f('ix_crawled_pages_content_hash'), 'crawled_pages', ['content_hash'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_crawled_pages_content_hash'), table_name='crawled_pages')
    op.drop_column('crawled_pages', 'content_hash')
    op.drop_index(op.f('ix_uploaded_files_content_hash'), table_name='uploaded_files')
    op.drop_column('uploaded_files', 'content_hash')
