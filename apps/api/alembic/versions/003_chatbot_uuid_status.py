"""
Update chatbots to use UUID id, status enum, welcome_message, soft delete.

Revision ID: 003_chatbot_uuid_status
Revises: 002_chatbots
Create Date: 2026-01-03
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003_chatbot_uuid_status"
down_revision: Union[str, None] = "002_chatbots"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgcrypto for gen_random_uuid
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # Create status enum
    chatbot_status_enum = postgresql.ENUM("draft", "active", "paused", name="chatbotstatus")
    chatbot_status_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns
    op.add_column("chatbots", sa.Column("welcome_message", sa.Text(), nullable=True))
    op.add_column(
        "chatbots",
        sa.Column(
            "status",
            chatbot_status_enum,
            nullable=False,
            server_default=sa.text("'draft'"),
        ),
    )
    op.add_column("chatbots", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # Add new UUID column, populate, then drop old integer id
    op.add_column(
        "chatbots",
        sa.Column(
            "id_new",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )
    # Drop existing FK from permissions before altering PK/ID
    op.execute(
        'ALTER TABLE chatbot_permissions DROP CONSTRAINT IF EXISTS chatbot_permissions_chatbot_id_fkey CASCADE'
    )

    # Replace chatbots.id with UUID
    op.drop_index(op.f("ix_chatbots_id"), table_name="chatbots")
    op.alter_column("chatbots", "id", new_column_name="id_old")
    op.alter_column("chatbots", "id_new", new_column_name="id")
    op.create_index(op.f("ix_chatbots_id"), "chatbots", ["id"], unique=False)
    op.drop_constraint("chatbots_pkey", "chatbots", type_="primary")
    op.create_primary_key("chatbots_pkey", "chatbots", ["id"])

    # Update chatbot_permissions to reference new id
    op.add_column(
        "chatbot_permissions",
        sa.Column(
            "chatbot_uuid",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.execute(
        "UPDATE chatbot_permissions cp "
        "SET chatbot_uuid = c.id "
        "FROM chatbots c WHERE cp.chatbot_id = c.id_old"
    )
    op.drop_index(op.f("ix_chatbot_permissions_chatbot_id"), table_name="chatbot_permissions")
    op.drop_column("chatbot_permissions", "chatbot_id")
    op.alter_column("chatbot_permissions", "chatbot_uuid", new_column_name="chatbot_id")
    op.create_index(op.f("ix_chatbot_permissions_chatbot_id"), "chatbot_permissions", ["chatbot_id"], unique=False)
    op.create_foreign_key(
        None,
        "chatbot_permissions",
        "chatbots",
        ["chatbot_id"],
        ["id"],
    )

    # Now drop old id column
    op.drop_column("chatbots", "id_old")


def downgrade() -> None:
    # Downgrade not supported safely; raise error
    raise RuntimeError("Downgrade not supported for UUID migration")

