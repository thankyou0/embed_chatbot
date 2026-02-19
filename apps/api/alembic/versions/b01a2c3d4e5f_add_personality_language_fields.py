"""add personality and language fields to chatbot_appearances

Revision ID: b01a2c3d4e5f
Revises: 027_add_hybrid_search_tsvector
Create Date: 2026-02-13 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b01a2c3d4e5f"
down_revision = "027_add_hybrid_search_tsvector"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add personality customization columns
    op.add_column(
        "chatbot_appearances",
        sa.Column(
            "personality_tone", sa.String(20), nullable=False, server_default="friendly"
        ),
    )
    op.add_column(
        "chatbot_appearances",
        sa.Column(
            "response_length", sa.String(20), nullable=False, server_default="balanced"
        ),
    )
    op.add_column(
        "chatbot_appearances",
        sa.Column("temperature", sa.Float(), nullable=False, server_default="0.7"),
    )
    op.add_column(
        "chatbot_appearances",
        sa.Column("custom_instructions", sa.Text(), nullable=True),
    )

    # Add language column
    op.add_column(
        "chatbot_appearances",
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
    )


def downgrade() -> None:
    # Remove the new columns
    op.drop_column("chatbot_appearances", "language")
    op.drop_column("chatbot_appearances", "custom_instructions")
    op.drop_column("chatbot_appearances", "temperature")
    op.drop_column("chatbot_appearances", "response_length")
    op.drop_column("chatbot_appearances", "personality_tone")
