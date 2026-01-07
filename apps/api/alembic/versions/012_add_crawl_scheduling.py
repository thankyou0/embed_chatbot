"""add crawl scheduling

Revision ID: 012_add_crawl_scheduling
Revises: 011_analytics
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '012_add_crawl_scheduling'
down_revision = '011_analytics'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types for scheduling
    op.execute("CREATE TYPE scheduletype AS ENUM ('manual', 'daily', 'weekly', 'monthly')")
    op.execute("CREATE TYPE crawlstatus AS ENUM ('success', 'partial', 'failed')")
    
    # Create crawl_schedules table
    op.create_table(
        'crawl_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('knowledge_source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('schedule_type', postgresql.ENUM('manual', 'daily', 'weekly', 'monthly', name='scheduletype', create_type=False), nullable=False, server_default='manual'),
        sa.Column('day_of_week', sa.Integer(), nullable=True),  # 0-6 for weekly
        sa.Column('preferred_hour', sa.Integer(), nullable=False, server_default='2'),  # 0-23, UTC
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_crawl_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_crawl_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['knowledge_source_id'], ['knowledge_sources.id'], ondelete='CASCADE'),
    )
    
    op.create_index(op.f('ix_crawl_schedules_id'), 'crawl_schedules', ['id'], unique=False)
    op.create_index(op.f('ix_crawl_schedules_knowledge_source_id'), 'crawl_schedules', ['knowledge_source_id'], unique=True)
    op.create_index(op.f('ix_crawl_schedules_next_crawl_at'), 'crawl_schedules', ['next_crawl_at'], unique=False)
    
    # Create crawl_history table
    op.create_table(
        'crawl_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('knowledge_source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', postgresql.ENUM('success', 'partial', 'failed', name='crawlstatus', create_type=False), nullable=False),
        sa.Column('pages_checked', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pages_added', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pages_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pages_removed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['knowledge_source_id'], ['knowledge_sources.id'], ondelete='CASCADE'),
    )
    
    op.create_index(op.f('ix_crawl_history_id'), 'crawl_history', ['id'], unique=False)
    op.create_index(op.f('ix_crawl_history_knowledge_source_id'), 'crawl_history', ['knowledge_source_id'], unique=False)
    op.create_index(op.f('ix_crawl_history_started_at'), 'crawl_history', ['started_at'], unique=False)
    
    # Add is_removed column to crawled_pages for soft delete
    op.add_column('crawled_pages', sa.Column('is_removed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('crawled_pages', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')))


def downgrade() -> None:
    # Remove columns from crawled_pages
    op.drop_column('crawled_pages', 'updated_at')
    op.drop_column('crawled_pages', 'is_removed')
    
    # Drop tables
    op.drop_index(op.f('ix_crawl_history_started_at'), table_name='crawl_history')
    op.drop_index(op.f('ix_crawl_history_knowledge_source_id'), table_name='crawl_history')
    op.drop_index(op.f('ix_crawl_history_id'), table_name='crawl_history')
    op.drop_table('crawl_history')
    
    op.drop_index(op.f('ix_crawl_schedules_next_crawl_at'), table_name='crawl_schedules')
    op.drop_index(op.f('ix_crawl_schedules_knowledge_source_id'), table_name='crawl_schedules')
    op.drop_index(op.f('ix_crawl_schedules_id'), table_name='crawl_schedules')
    op.drop_table('crawl_schedules')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS crawlstatus")
    op.execute("DROP TYPE IF EXISTS scheduletype")

