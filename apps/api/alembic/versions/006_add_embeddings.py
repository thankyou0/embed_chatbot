"""Add embeddings table and pgvector extension

Revision ID: 006_embeddings
Revises: 005_knowledge
Create Date: 2026-01-03 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '006_embeddings'
down_revision: Union[str, None] = '005_knowledge'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create embeddings table
    # Use postgresql.ENUM with create_type=False to reference the existing ENUM from migration 005
    source_type_enum = postgresql.ENUM('crawled_url', 'uploaded_file', 'qa_pair', name='knowledgesourcetype', create_type=False)
    
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('chatbot_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('knowledge_source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_type', source_type_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('priority_weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['knowledge_source_id'], ['knowledge_sources.id'], ondelete='CASCADE'),
    )
    
    op.create_index(op.f('ix_embeddings_id'), 'embeddings', ['id'], unique=False)
    op.create_index(op.f('ix_embeddings_chatbot_id'), 'embeddings', ['chatbot_id'], unique=False)
    op.create_index(op.f('ix_embeddings_knowledge_source_id'), 'embeddings', ['knowledge_source_id'], unique=False)

    # Add HNSW index for vector similarity search (optional but recommended for large datasets)
    # op.execute('CREATE INDEX idx_embeddings_vector ON embeddings USING hnsw (embedding vector_cosine_ops)')


def downgrade() -> None:
    op.drop_index(op.f('ix_embeddings_knowledge_source_id'), table_name='embeddings')
    op.drop_index(op.f('ix_embeddings_chatbot_id'), table_name='embeddings')
    op.drop_index(op.f('ix_embeddings_id'), table_name='embeddings')
    op.drop_table('embeddings')
    
    # We might not want to drop the extension if other tables use it
    # op.execute('DROP EXTENSION IF EXISTS vector')

