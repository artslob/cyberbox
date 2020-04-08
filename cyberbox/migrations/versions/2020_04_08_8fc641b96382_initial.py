"""initial

Revision ID: 8fc641b96382
Revises:
Create Date: 2020-04-08 18:33:40.327225+00:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "8fc641b96382"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("uid", postgresql.UUID(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("disabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_user")),
        sa.UniqueConstraint("username", name=op.f("uq_user_username")),
    )
    op.create_table(
        "file",
        sa.Column("uid", postgresql.UUID(), nullable=False),
        sa.Column("owner", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner"], ["user.username"], name=op.f("fk_file_owner_user_username")
        ),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_file")),
    )
    op.create_table(
        "link",
        sa.Column("uid", postgresql.UUID(), nullable=True),
        sa.Column("link", sa.String(), nullable=False),
        sa.Column("is_onetime", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("visited_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("valid_until", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["uid"], ["file.uid"], name=op.f("fk_link_uid_file_uid")),
        sa.UniqueConstraint("link", name=op.f("uq_link_link")),
    )


def downgrade():
    op.drop_table("link")
    op.drop_table("file")
    op.drop_table("user")
