"""Add crawl_notifications table and crawl_progress column

Revision ID: 031_crawl_notifications
Revises: 030_add_scope_description
Create Date: 2026-02-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers
revision = "031_crawl_notifications"
down_revision = "030_add_scope_description"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add crawl_progress JSONB column to knowledge_sources
    op.add_column(
        "knowledge_sources",
        sa.Column("crawl_progress", JSONB, nullable=True),
    )

    # 2. Create crawl_notifications table
    op.create_table(
        "crawl_notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column(
            "knowledge_source_id",
            UUID(as_uuid=True),
            sa.ForeignKey("knowledge_sources.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false", index=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
    )

    # 3. Index for quick lookup: unread notifications per knowledge source
    op.create_index(
        "ix_crawl_notifications_ks_unread",
        "crawl_notifications",
        ["knowledge_source_id", "is_read"],
        postgresql_where=sa.text("is_read = false"),
    )


def downgrade():
    op.drop_index("ix_crawl_notifications_ks_unread", table_name="crawl_notifications")
    op.drop_table("crawl_notifications")
    op.drop_column("knowledge_sources", "crawl_progress")
