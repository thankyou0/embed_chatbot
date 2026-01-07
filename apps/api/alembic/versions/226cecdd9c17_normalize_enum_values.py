"""normalize_enum_values

Revision ID: 226cecdd9c17
Revises: 8ddec77c0a72
Create Date: 2026-01-06 17:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '226cecdd9c17'
down_revision: Union[str, None] = '8ddec77c0a72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename PermissionLevel values to lowercase
    with op.get_context().autocommit_block():
        for val in ['OWNER', 'ADMIN', 'EDITOR', 'VIEWER']:
            op.execute(f"ALTER TYPE permissionlevel RENAME VALUE '{val}' TO '{val.lower()}'")
        
        # Rename UserRole values to lowercase
        for val in ['ADMIN', 'USER']:
            op.execute(f"ALTER TYPE userrole RENAME VALUE '{val}' TO '{val.lower()}'")

    # Fix granular permissions that were missed in the previous migration due to case mismatch
    op.execute("""
        UPDATE chatbot_permissions 
        SET can_manage_knowledge = true, 
            can_manage_appearance = true, 
            can_resolve_queries = true, 
            can_view_analytics = true 
        WHERE permission_level::text IN ('owner', 'admin')
    """)
    op.execute("""
        UPDATE chatbot_permissions 
        SET can_manage_knowledge = true, 
            can_resolve_queries = true, 
            can_view_analytics = true 
        WHERE permission_level::text = 'editor'
    """)


def downgrade() -> None:
    # Rename values back to uppercase
    with op.get_context().autocommit_block():
        for val in ['owner', 'admin', 'editor', 'viewer']:
            op.execute(f"ALTER TYPE permissionlevel RENAME VALUE '{val}' TO '{val.upper()}'")
        
        for val in ['admin', 'user']:
            op.execute(f"ALTER TYPE userrole RENAME VALUE '{val}' TO '{val.upper()}'")
