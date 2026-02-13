"""Add subscription and billing tables

Revision ID: 022_add_subscriptions
Revises: 021_add_content_hash
Create Date: 2026-01-31 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid


# revision identifiers, used by Alembic.
revision = '022_add_subscriptions'
down_revision = '021_add_content_hash'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums
    plantype_enum = ENUM('free', 'pro', 'enterprise', name='plantype', create_type=False)
    plantype_enum.create(op.get_bind(), checkfirst=True)
    
    billingcycle_enum = ENUM('monthly', 'annual', name='billingcycle', create_type=False)
    billingcycle_enum.create(op.get_bind(), checkfirst=True)
    
    subscriptionstatus_enum = ENUM('active', 'cancelled', 'expired', 'trialing', name='subscriptionstatus', create_type=False)
    subscriptionstatus_enum.create(op.get_bind(), checkfirst=True)
    
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', sa.Integer(), nullable=False, unique=True, index=True),
        sa.Column('plan_type', plantype_enum, nullable=False, server_default='free'),
        sa.Column('billing_cycle', billingcycle_enum, nullable=True),
        sa.Column('status', subscriptionstatus_enum, nullable=False, server_default='active'),
        sa.Column('current_period_start', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    
    # Create usage_records table
    op.create_table(
        'usage_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('subscription_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('chatbots_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('messages_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conversations_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('knowledge_pages_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('knowledge_files_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('team_members_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('api_calls_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('storage_mb', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
    )
    
    # Create billing_history table
    op.create_table(
        'billing_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('subscription_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('payment_status', sa.String(50), nullable=False, server_default='paid'),
        sa.Column('billing_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('billing_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
    )
    
    # Create default subscriptions for existing tenants
    op.execute("""
        INSERT INTO subscriptions (id, tenant_id, plan_type, status, current_period_start, current_period_end)
        SELECT 
            gen_random_uuid(),
            id,
            'free',
            'active',
            NOW(),
            NOW() + INTERVAL '1 month'
        FROM tenants
        WHERE NOT EXISTS (
            SELECT 1 FROM subscriptions WHERE subscriptions.tenant_id = tenants.id
        )
    """)


def downgrade():
    op.drop_table('billing_history')
    op.drop_table('usage_records')
    op.drop_table('subscriptions')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS subscriptionstatus')
    op.execute('DROP TYPE IF EXISTS billingcycle')
    op.execute('DROP TYPE IF EXISTS plantype')
