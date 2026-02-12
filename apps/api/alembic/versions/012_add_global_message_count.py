"""Add global message count tracking

Revision ID: 023_global_message_count
Revises: 022_add_subscriptions
Create Date: 2026-02-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '023_global_message_count'
down_revision: Union[str, None] = '022_add_subscriptions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add global_message_count to subscriptions table (persists even after bot deletion)
    op.add_column('subscriptions', sa.Column('global_message_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Add per-chatbot message count
    op.add_column('chatbots', sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Create indexes for better performance
    op.create_index('ix_subscriptions_global_message_count', 'subscriptions', ['global_message_count'])
    op.create_index('ix_chatbots_message_count', 'chatbots', ['message_count'])


def downgrade() -> None:
    op.drop_index('ix_subscriptions_global_message_count', 'subscriptions')
    op.drop_index('ix_chatbots_message_count', 'chatbots')
    op.drop_column('subscriptions', 'global_message_count')
    op.drop_column('chatbots', 'message_count')
