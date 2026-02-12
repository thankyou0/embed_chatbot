"""Add chatbot activities table

Revision ID: 014_add_chatbot_activities
Revises: 013_member_permissions
Create Date: 2026-01-06 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '014_add_chatbot_activities'
down_revision: Union[str, None] = '013_member_permissions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create chatbot_activities table
    op.create_table(
        'chatbot_activities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('chatbot_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chatbot_id'], ['chatbots.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chatbot_activities_chatbot_id'), 'chatbot_activities', ['chatbot_id'], unique=False)
    op.create_index(op.f('ix_chatbot_activities_id'), 'chatbot_activities', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_chatbot_activities_id'), table_name='chatbot_activities')
    op.drop_index(op.f('ix_chatbot_activities_chatbot_id'), table_name='chatbot_activities')
    op.drop_table('chatbot_activities')
