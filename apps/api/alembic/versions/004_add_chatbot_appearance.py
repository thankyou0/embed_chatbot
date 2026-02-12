"""Add chatbot appearance table

Revision ID: 004_appearance
Revises: 003_chatbot_uuid_status
Create Date: 2026-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_appearance'
down_revision: Union[str, None] = '003_chatbot_uuid_status'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create widget position enum if it doesn't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE widgetposition AS ENUM ('bottom-right', 'bottom-left');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create chatbot_appearances table
    op.create_table(
        'chatbot_appearances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('chatbot_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('primary_color', sa.String(50), nullable=False, server_default='#2563eb'),
        sa.Column('header_text', sa.String(255), nullable=False, server_default='Chat with us'),
        sa.Column('avatar_url', sa.String(1024), nullable=True),
        sa.Column('position', postgresql.ENUM('bottom-right', 'bottom-left', name='widgetposition', create_type=False), nullable=False, server_default='bottom-right'),
        sa.Column('welcome_message', sa.Text(), nullable=True),
        sa.Column('initial_suggestions', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('show_branding', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ondelete='CASCADE'),
    )
    
    op.create_index(op.f('ix_chatbot_appearances_id'), 'chatbot_appearances', ['id'], unique=False)
    op.create_index(op.f('ix_chatbot_appearances_chatbot_id'), 'chatbot_appearances', ['chatbot_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_chatbot_appearances_chatbot_id'), table_name='chatbot_appearances')
    op.drop_index(op.f('ix_chatbot_appearances_id'), table_name='chatbot_appearances')
    op.drop_table('chatbot_appearances')
    
    # Drop enum
    op.execute('DROP TYPE IF EXISTS widgetposition')

