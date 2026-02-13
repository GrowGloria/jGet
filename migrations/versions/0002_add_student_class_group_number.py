"""add student class and group number

Revision ID: 0002_add_student_class_group_number
Revises: 0001_init
Create Date: 2026-02-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_student_class_group_number"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("students", sa.Column("school_class", sa.String(50), nullable=True))
    op.add_column("students", sa.Column("group_number", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("students", "group_number")
    op.drop_column("students", "school_class")
