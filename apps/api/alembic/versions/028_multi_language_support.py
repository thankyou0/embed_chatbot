"""Convert language column from single string to JSONB array for multi-language support

Revision ID: 028_multi_language_support
Revises: b01a2c3d4e5f
Create Date: 2026-02-14

This migration:
1. Converts the `language` column in chatbot_appearances from String to JSONB
2. Migrates existing single values ("en") to arrays (["en"])
3. All existing chatbots keep their current language as the only selected language
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = "028_multi_language_support"
down_revision = "b01a2c3d4e5f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add a new temporary JSONB column
    op.add_column(
        "chatbot_appearances",
        sa.Column("languages", JSONB, nullable=True),
    )

    # Step 2: Migrate existing data - convert single string to JSON array
    # e.g., "en" -> ["en"], "hi" -> ["hi"], "gu" -> ["gu"]
    op.execute(
        """
        UPDATE chatbot_appearances 
        SET languages = CASE 
            WHEN language IS NOT NULL AND language != '' 
            THEN jsonb_build_array(language)
            ELSE '["en"]'::jsonb
        END
        """
    )

    # Step 3: Set NOT NULL and default on new column
    op.alter_column(
        "chatbot_appearances",
        "languages",
        nullable=False,
        server_default=sa.text("'[\"en\"]'::jsonb"),
    )

    # Step 4: Drop the old language column
    op.drop_column("chatbot_appearances", "language")


def downgrade() -> None:
    # Step 1: Add back the old string column
    op.add_column(
        "chatbot_appearances",
        sa.Column("language", sa.String(10), nullable=True, server_default="en"),
    )

    # Step 2: Migrate back - take the first element of the array
    op.execute(
        """
        UPDATE chatbot_appearances 
        SET language = COALESCE(languages->>0, 'en')
        """
    )

    # Step 3: Set NOT NULL
    op.alter_column(
        "chatbot_appearances",
        "language",
        nullable=False,
    )

    # Step 4: Drop the JSONB column
    op.drop_column("chatbot_appearances", "languages")
