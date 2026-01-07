"""Add qa_pairs table

Revision ID: 008_qa_pairs
Revises: 007_uploaded_files
Create Date: 2026-01-03 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '008_qa_pairs'
down_revision: Union[str, None] = '007_uploaded_files'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create qa_pairs table
    op.create_table(
        'qa_pairs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('knowledge_source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['knowledge_source_id'], ['knowledge_sources.id'], ondelete='CASCADE'),
    )
    
    op.create_index(op.f('ix_qa_pairs_id'), 'qa_pairs', ['id'], unique=False)
    op.create_index(op.f('ix_qa_pairs_knowledge_source_id'), 'qa_pairs', ['knowledge_source_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_qa_pairs_knowledge_source_id'), table_name='qa_pairs')
    op.drop_index(op.f('ix_qa_pairs_id'), table_name='qa_pairs')
    op.drop_table('qa_pairs')

