"""Add scope_description JSONB column to chatbots

Revision ID: 030_add_scope_description
Revises: 029_add_welcome_translations
Create Date: 2026-02-23

Auto-generated chatbot scope description from crawl data.
Stores: brand_name, business_type, what_they_sell, topics_covered, not_about, auto_generated, last_updated.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "030_add_scope_description"
down_revision = "029_add_welcome_translations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chatbots",
        sa.Column("scope_description", JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("chatbots", "scope_description")
