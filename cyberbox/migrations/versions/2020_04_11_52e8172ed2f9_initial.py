"""initial

Revision ID: 52e8172ed2f9
Revises:
Create Date: 2020-04-11 10:49:25.620713+00:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "52e8172ed2f9"
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
    op.create_index(op.f("ix_user_created"), "user", ["created"], unique=False)
    op.create_table(
        "file",
        sa.Column("uid", postgresql.UUID(), nullable=False),
        sa.Column("owner", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner"],
            ["user.username"],
            name=op.f("fk_file_owner_user_username"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_file")),
    )
    op.create_index(op.f("ix_file_created"), "file", ["created"], unique=False)
    op.create_index(op.f("ix_file_owner"), "file", ["owner"], unique=False)
    op.create_table(
        "link",
        sa.Column("uid", postgresql.UUID(), nullable=False),
        sa.Column("link", sa.String(), nullable=False),
        sa.Column("is_onetime", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("visited_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("valid_until", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["uid"],
            ["file.uid"],
            name=op.f("fk_link_uid_file_uid"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("link", name=op.f("pk_link")),
    )
    op.create_index(op.f("ix_link_created"), "link", ["created"], unique=False)
    op.create_index(op.f("ix_link_uid"), "link", ["uid"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_link_uid"), table_name="link")
    op.drop_index(op.f("ix_link_created"), table_name="link")
    op.drop_table("link")
    op.drop_index(op.f("ix_file_owner"), table_name="file")
    op.drop_index(op.f("ix_file_created"), table_name="file")
    op.drop_table("file")
    op.drop_index(op.f("ix_user_created"), table_name="user")
    op.drop_table("user")
