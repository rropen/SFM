"""first migration

Revision ID: 1d3daaeebc36
Revises:
Create Date: 2021-05-14 03:12:44.918520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1d3daaeebc36"
down_revision = None
branch_labels = None
depends_on = None


def downgrade():
    pass


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "workItems",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("category", sa.VARCHAR(), nullable=False),
        sa.Column("start_time", sa.DATETIME(), nullable=True),
        sa.Column("end_time", sa.DATETIME(), nullable=True),
        sa.Column("duration_open", sa.DATETIME(), nullable=True),
        sa.Column("comments", sa.VARCHAR(), nullable=True),
        sa.Column("project_id", sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=True),
        sa.Column("lead_name", sa.VARCHAR(), nullable=True),
        sa.Column("lead_email", sa.VARCHAR(), nullable=True),
        sa.Column("description", sa.VARCHAR(), nullable=True),
        sa.Column("location", sa.VARCHAR(), nullable=False),
        sa.Column("repo_url", sa.VARCHAR(), nullable=False),
        sa.Column("on_prem", sa.BOOLEAN(), nullable=False),
    )
    # op.create_index("ix_workItems_id", "workItems", ["id"], unique=True)
    # ### end Alembic commands ###
