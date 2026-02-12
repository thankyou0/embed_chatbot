"""Enable HNSW vector index for fast similarity search

Revision ID: 025_enable_hnsw_index
Revises: 024_add_org_owner_analytics
Create Date: 2026-02-12 00:00:00.000000

HNSW (Hierarchical Navigable Small World) index provides 10-50x faster
cosine similarity search for >10k embeddings compared to sequential scan.

This is safe to add on a live table — PostgreSQL creates the index
without blocking reads/writes (though building may take time on large datasets).
"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '025_enable_hnsw_index'
down_revision: Union[str, None] = '024_add_org_owner_analytics'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create HNSW index for fast vector cosine similarity search
    # vector_cosine_ops is the correct operator class for cosine distance queries
    # m=16, ef_construction=64 are good defaults for balanced speed/recall
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_embeddings_vector_hnsw
        ON embeddings
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_embeddings_vector_hnsw")
