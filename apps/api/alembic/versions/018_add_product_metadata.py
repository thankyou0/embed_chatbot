"""Add product_metadata to crawled_pages

Revision ID: 018_add_product_metadata
Revises: 96f9c273fa63
Create Date: 2026-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '018_add_product_metadata'
down_revision: Union[str, None] = '96f9c273fa63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add product_metadata column to crawled_pages table
    op.add_column(
        'crawled_pages',
        sa.Column('product_metadata', JSONB, nullable=True)
    )
    
    # Add is_product column for quick filtering
    op.add_column(
        'crawled_pages',
        sa.Column('is_product', sa.Boolean, nullable=False, server_default='false')
    )
    
    # Create index on is_product for efficient filtering
    op.create_index(
        'ix_crawled_pages_is_product',
        'crawled_pages',
        ['is_product']
    )


def downgrade() -> None:
    op.drop_index('ix_crawled_pages_is_product', table_name='crawled_pages')
    op.drop_column('crawled_pages', 'is_product')
    op.drop_column('crawled_pages', 'product_metadata')
