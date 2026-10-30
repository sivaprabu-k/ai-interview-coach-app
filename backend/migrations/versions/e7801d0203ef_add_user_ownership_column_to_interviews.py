
"""add user ownership column to interviews"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e7801d0203ef"
down_revision: Union[str, Sequence[str], None] = "82aa4e0ee619"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "interviews",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_interviews_user_id",
        "interviews",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_interviews_user_id_users",
        "interviews",
        "users",
        ["user_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_interviews_user_id_users",
        "interviews",
        type_="foreignkey",
    )
    op.drop_index("ix_interviews_user_id", table_name="interviews")
    op.drop_column("interviews", "user_id")
