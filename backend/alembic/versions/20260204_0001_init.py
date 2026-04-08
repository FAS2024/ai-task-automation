from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260204_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "task_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("client_id", sa.String(length=128), nullable=False),
        sa.Column("workflow_type", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_task_runs_task_id", "task_runs", ["task_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_task_runs_task_id", table_name="task_runs")
    op.drop_table("task_runs")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
