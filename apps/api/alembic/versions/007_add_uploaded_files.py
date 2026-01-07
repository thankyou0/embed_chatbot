"""Add uploaded_files table

Revision ID: 007_uploaded_files
Revises: 006_embeddings
Create Date: 2026-01-03 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007_uploaded_files'
down_revision: Union[str, None] = '006_embeddings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create uploaded_files table
    op.create_table(
        'uploaded_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('knowledge_source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(1024), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['knowledge_source_id'], ['knowledge_sources.id'], ondelete='CASCADE'),
    )
    
    op.create_index(op.f('ix_uploaded_files_id'), 'uploaded_files', ['id'], unique=False)
    op.create_index(op.f('ix_uploaded_files_knowledge_source_id'), 'uploaded_files', ['knowledge_source_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_uploaded_files_knowledge_source_id'), table_name='uploaded_files')
    op.drop_index(op.f('ix_uploaded_files_id'), table_name='uploaded_files')
    op.drop_table('uploaded_files')

