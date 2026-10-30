"""create users table

Revision ID: b8581cd43931
Revises: 82aa4e0ee619
Create Date: 2026-10-29 15:37:16.172435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8581cd43931'
down_revision: Union[str, Sequence[str], None] = 'cbe23fce7ce8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
