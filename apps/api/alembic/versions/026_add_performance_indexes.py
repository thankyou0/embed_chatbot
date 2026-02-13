"""add performance indexes

Revision ID: 026_add_performance_indexes
Revises: 025_enable_hnsw_index
Create Date: 2026-02-13

Critical performance indexes for analytics and billing queries
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "026_add_performance_indexes"
down_revision = "025_enable_hnsw_index"
branch_labels = None
depends_on = None


def upgrade():
    """Add critical performance indexes"""

    # Chat sessions indexes - heavily queried for analytics/billing
    op.create_index(
        "ix_chat_sessions_started_at",
        "chat_sessions",
        ["started_at"],
        postgresql_using="btree",
    )

    op.create_index(
        "ix_chat_sessions_is_preview",
        "chat_sessions",
        ["is_preview"],
        postgresql_using="btree",
    )

    # Composite index for common query pattern
    op.create_index(
        "ix_chat_sessions_chatbot_started_preview",
        "chat_sessions",
        ["chatbot_id", "started_at", "is_preview"],
        postgresql_using="btree",
    )

    # Chat messages indexes - filtered frequently
    op.create_index(
        "ix_chat_messages_role", "chat_messages", ["role"], postgresql_using="btree"
    )

    op.create_index(
        "ix_chat_messages_created_at",
        "chat_messages",
        ["created_at"],
        postgresql_using="btree",
    )

    # Composite index for session message queries
    op.create_index(
        "ix_chat_messages_session_created_role",
        "chat_messages",
        ["session_id", "created_at", "role"],
        postgresql_using="btree",
    )

    # Chatbots deleted_at index - filtered in every query
    op.create_index(
        "ix_chatbots_deleted_at", "chatbots", ["deleted_at"], postgresql_using="btree"
    )

    # Composite index for tenant chatbot queries
    op.create_index(
        "ix_chatbots_tenant_deleted",
        "chatbots",
        ["tenant_id", "deleted_at"],
        postgresql_using="btree",
    )

    # Knowledge sources indexes
    op.create_index(
        "ix_crawled_pages_is_removed",
        "crawled_pages",
        ["is_removed"],
        postgresql_using="btree",
    )

    # Composite index for knowledge queries
    op.create_index(
        "ix_crawled_pages_ks_removed",
        "crawled_pages",
        ["knowledge_source_id", "is_removed"],
        postgresql_using="btree",
    )

    # JSONB GIN index for metadata searches (analytics)
    op.create_index(
        "ix_chat_messages_metadata_gin",
        "chat_messages",
        ["metadata_json"],
        postgresql_using="gin",
    )


def downgrade():
    """Remove performance indexes"""
    op.drop_index("ix_chat_messages_metadata_gin", table_name="chat_messages")
    op.drop_index("ix_crawled_pages_ks_removed", table_name="crawled_pages")
    op.drop_index("ix_crawled_pages_is_removed", table_name="crawled_pages")
    op.drop_index("ix_chatbots_tenant_deleted", table_name="chatbots")
    op.drop_index("ix_chatbots_deleted_at", table_name="chatbots")
    op.drop_index("ix_chat_messages_session_created_role", table_name="chat_messages")
    op.drop_index("ix_chat_messages_created_at", table_name="chat_messages")
    op.drop_index("ix_chat_messages_role", table_name="chat_messages")
    op.drop_index(
        "ix_chat_sessions_chatbot_started_preview", table_name="chat_sessions"
    )
    op.drop_index("ix_chat_sessions_is_preview", table_name="chat_sessions")
    op.drop_index("ix_chat_sessions_started_at", table_name="chat_sessions")
