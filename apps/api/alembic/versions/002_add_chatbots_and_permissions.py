"""Add chatbots and permissions

Revision ID: 002_chatbots
Revises: 001_initial
Create Date: 2025-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_chatbots'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    
    # Create chatbots table
    op.create_table(
        'chatbots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chatbots_id'), 'chatbots', ['id'], unique=False)
    op.create_index(op.f('ix_chatbots_tenant_id'), 'chatbots', ['tenant_id'], unique=False)
    
    # Create permission level enum
    permission_enum = postgresql.ENUM('OWNER', 'ADMIN', 'EDITOR', 'VIEWER', name='permissionlevel', create_type=False)
    permission_enum.create(op.get_bind(), checkfirst=True)
    
    # Create chatbot_permissions table using raw SQL to avoid enum auto-creation issues
    op.execute("""
        CREATE TABLE chatbot_permissions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            chatbot_id INTEGER NOT NULL REFERENCES chatbots(id),
            permission_level permissionlevel NOT NULL,
            granted_by INTEGER NOT NULL REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            UNIQUE(user_id, chatbot_id)
        )
    """)
    op.create_index(op.f('ix_chatbot_permissions_id'), 'chatbot_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_chatbot_permissions_user_id'), 'chatbot_permissions', ['user_id'], unique=False)
    op.create_index(op.f('ix_chatbot_permissions_chatbot_id'), 'chatbot_permissions', ['chatbot_id'], unique=False)


def downgrade() -> None:
    # Drop chatbot_permissions
    op.drop_index(op.f('ix_chatbot_permissions_chatbot_id'), table_name='chatbot_permissions')
    op.drop_index(op.f('ix_chatbot_permissions_user_id'), table_name='chatbot_permissions')
    op.drop_index(op.f('ix_chatbot_permissions_id'), table_name='chatbot_permissions')
    op.drop_table('chatbot_permissions')
    
    # Drop chatbots
    op.drop_index(op.f('ix_chatbots_tenant_id'), table_name='chatbots')
    op.drop_index(op.f('ix_chatbots_id'), table_name='chatbots')
    op.drop_table('chatbots')
    
    # Drop permission level enum
    op.execute('DROP TYPE IF EXISTS permissionlevel')
    
    # Remove columns from users
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'name')

