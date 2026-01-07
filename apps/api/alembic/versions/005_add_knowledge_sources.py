"""Add knowledge sources and crawled pages

Revision ID: 005_knowledge
Revises: 004_appearance
Create Date: 2026-01-03 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005_knowledge'
down_revision: Union[str, None] = '004_appearance'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
   # 1. Clean up any existing types from previous failed attempts
    op.execute("DROP TYPE IF EXISTS knowledgesourcetype CASCADE")
    op.execute("DROP TYPE IF EXISTS knowledgesourcestatus CASCADE")
    
    # 2. Re-create them clean
    op.execute("CREATE TYPE knowledgesourcetype AS ENUM ('crawled_url', 'uploaded_file', 'qa_pair')")
    op.execute("CREATE TYPE knowledgesourcestatus AS ENUM ('pending', 'crawling', 'completed', 'failed')")
    
    
    # Create knowledge_sources table
    op.create_table(
        'knowledge_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('chatbot_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_type', postgresql.ENUM('crawled_url', 'uploaded_file', 'qa_pair', name='knowledgesourcetype', create_type=False), nullable=False),
        sa.Column('source_url', sa.String(2048), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'crawling', 'completed', 'failed', name='knowledgesourcestatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('pages_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ondelete='CASCADE'),
    )
    
    op.create_index(op.f('ix_knowledge_sources_id'), 'knowledge_sources', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_sources_chatbot_id'), 'knowledge_sources', ['chatbot_id'], unique=False)

    # Create crawled_pages table
    op.create_table(
        'crawled_pages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('knowledge_source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(2048), nullable=False),
        sa.Column('title', sa.String(1024), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['knowledge_source_id'], ['knowledge_sources.id'], ondelete='CASCADE'),
    )
    
    op.create_index(op.f('ix_crawled_pages_id'), 'crawled_pages', ['id'], unique=False)
    op.create_index(op.f('ix_crawled_pages_knowledge_source_id'), 'crawled_pages', ['knowledge_source_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_crawled_pages_knowledge_source_id'), table_name='crawled_pages')
    op.drop_index(op.f('ix_crawled_pages_id'), table_name='crawled_pages')
    op.drop_table('crawled_pages')
    
    op.drop_index(op.f('ix_knowledge_sources_chatbot_id'), table_name='knowledge_sources')
    op.drop_index(op.f('ix_knowledge_sources_id'), table_name='knowledge_sources')
    op.drop_table('knowledge_sources')
    
    op.execute('DROP TYPE IF EXISTS knowledgesourcestatus')
    op.execute('DROP TYPE IF EXISTS knowledgesourcetype')

