"""Add is_org_owner to users and rename can_view_analytics to can_view_analytics_billing

Revision ID: 024_add_org_owner_analytics
Revises: 023_global_message_count
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '024_add_org_owner_analytics'
down_revision = '023_global_message_count'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_org_owner column to users table
    op.add_column('users', sa.Column('is_org_owner', sa.Boolean(), nullable=True, server_default='false'))
    
    # Update existing users: the first user in each tenant (by created_at) is the org owner
    # This is done using a correlated subquery
    op.execute("""
        UPDATE users 
        SET is_org_owner = true 
        WHERE id IN (
            SELECT DISTINCT ON (tenant_id) id 
            FROM users 
            ORDER BY tenant_id, created_at ASC
        )
    """)
    
    # Now make it not nullable
    op.alter_column('users', 'is_org_owner', nullable=False, server_default='false')
    
    # Rename can_view_analytics to can_view_analytics_billing in chatbot_permissions
    op.alter_column('chatbot_permissions', 'can_view_analytics', new_column_name='can_view_analytics_billing')


def downgrade() -> None:
    # Rename back can_view_analytics_billing to can_view_analytics
    op.alter_column('chatbot_permissions', 'can_view_analytics_billing', new_column_name='can_view_analytics')
    
    # Drop is_org_owner column
    op.drop_column('users', 'is_org_owner')
