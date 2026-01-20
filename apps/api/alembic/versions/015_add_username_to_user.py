"""add username to user

Revision ID: 015_add_username_to_user
Revises: 8ddec77c0a72
Create Date: 2026-01-09 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '015_add_username_to_user'
down_revision: Union[str, None] = '226cecdd9c17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Add username column as nullable first to handle existing users
    op.add_column('users', sa.Column('username', sa.String(length=255), nullable=True))
    
    # 2. Update existing users to have a username based on their email
    op.execute("UPDATE users SET username = email WHERE username IS NULL")
    
    # 3. Make username NOT NULL and UNIQUE
    op.alter_column('users', 'username', nullable=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'username')