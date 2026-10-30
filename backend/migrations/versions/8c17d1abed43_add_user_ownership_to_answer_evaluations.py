
"""add user ownership to answer evaluations

Revision ID: 8c17d1abed43
Revises: 7d7ef3e952f1
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c17d1abed43"
down_revision: Union[str, Sequence[str], None] = "7d7ef3e952f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "answer_evaluations",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    op.create_index(
        "ix_answer_evaluations_user_id",
        "answer_evaluations",
        ["user_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_answer_evaluations_user_id_users",
        "answer_evaluations",
        "users",
        ["user_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_answer_evaluations_user_id_users",
        "answer_evaluations",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_answer_evaluations_user_id",
        table_name="answer_evaluations",
    )

    op.drop_column("answer_evaluations", "user_id")
