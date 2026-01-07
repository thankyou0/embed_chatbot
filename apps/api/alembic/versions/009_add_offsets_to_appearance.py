"""Add offset_x and offset_y to chatbot_appearances

Revision ID: 009_add_offsets_to_appearance
Revises: 008_qa_pairs
Create Date: 2026-01-03 18:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '009_add_offsets_to_appearance'
down_revision: Union[str, None] = '008_qa_pairs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add offset_x and offset_y columns to chatbot_appearances
    op.add_column('chatbot_appearances', sa.Column('offset_x', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('chatbot_appearances', sa.Column('offset_y', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove offset_x and offset_y columns from chatbot_appearances
    op.drop_column('chatbot_appearances', 'offset_y')
    op.drop_column('chatbot_appearances', 'offset_x')

