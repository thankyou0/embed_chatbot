"""Add member permissions and temporary password fields

Revision ID: 013_member_permissions
Revises: 012_add_crawl_scheduling
Create Date: 2025-01-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '013_member_permissions'
down_revision: Union[str, None] = '012_add_crawl_scheduling'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add temporary password fields to users table
    op.add_column('users', sa.Column('password_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('invited_by', sa.Integer(), nullable=True))
    
    # Add foreign key constraint for invited_by
    op.create_foreign_key(
        'fk_users_invited_by',
        'users', 'users',
        ['invited_by'], ['id']
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_users_invited_by', 'users', type_='foreignkey')
    
    # Remove columns
    op.drop_column('users', 'invited_by')
    op.drop_column('users', 'must_change_password')
    op.drop_column('users', 'password_expires_at')

