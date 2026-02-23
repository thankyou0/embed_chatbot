"""Add welcome_message_translations JSONB column to chatbot_appearances

Revision ID: 029_add_welcome_translations
Revises: 028_multi_language_support
Create Date: 2026-02-15

Stores LLM-translated variants of the welcome message for each configured language.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "029_add_welcome_translations"
down_revision = "028_multi_language_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chatbot_appearances",
        sa.Column("welcome_message_translations", JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("chatbot_appearances", "welcome_message_translations")
