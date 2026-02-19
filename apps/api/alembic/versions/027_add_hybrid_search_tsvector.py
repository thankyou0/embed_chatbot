"""Add tsvector column for hybrid BM25+Vector search

Revision ID: 027_add_hybrid_search_tsvector
Revises: 026_add_performance_indexes
Create Date: 2026-02-13

This migration adds full-text search capability to embeddings table:
1. Adds a generated tsvector column for BM25-style keyword search
2. Creates a GIN index for fast text search
3. Enables hybrid search combining vector similarity with keyword matching

Benefits:
- Exact match for SKUs, product codes, model numbers
- Better recall for specific product names
- Combines semantic understanding (vector) with exact matching (BM25)
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "027_add_hybrid_search_tsvector"
down_revision = "026_add_performance_indexes"
branch_labels = None
depends_on = None


def upgrade():
    """Add tsvector column and GIN index for hybrid search"""
    
    # Add generated tsvector column
    # Using English configuration for stemming and stop words
    # The column is auto-generated from the content column
    op.execute("""
        ALTER TABLE embeddings 
        ADD COLUMN IF NOT EXISTS content_tsvector tsvector 
        GENERATED ALWAYS AS (to_tsvector('english', COALESCE(content, ''))) STORED
    """)
    
    # Create GIN index for fast full-text search
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_embeddings_content_tsvector 
        ON embeddings USING GIN(content_tsvector)
    """)
    
    # Create composite index for chatbot_id + tsvector for filtered searches
    # This helps when searching within a specific chatbot's knowledge base
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_embeddings_chatbot_tsvector 
        ON embeddings (chatbot_id) 
        WHERE content_tsvector IS NOT NULL
    """)


def downgrade():
    """Remove tsvector column and indexes"""
    
    # Drop indexes first
    op.execute("DROP INDEX IF EXISTS idx_embeddings_chatbot_tsvector")
    op.execute("DROP INDEX IF EXISTS idx_embeddings_content_tsvector")
    
    # Drop the column
    op.execute("ALTER TABLE embeddings DROP COLUMN IF EXISTS content_tsvector")
