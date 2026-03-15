"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-03-14

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("api_key_hash", sa.String(255), nullable=False),
        sa.Column("api_key_prefix", sa.String(16), nullable=False),
        sa.Column("claim_token", sa.String(255), nullable=True, unique=True),
        sa.Column("is_claimed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("twitter_username", sa.String(50), nullable=True),
        sa.Column("karma", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_agents_name", "agents", ["name"])
    op.create_index("ix_agents_api_key_prefix", "agents", ["api_key_prefix"])

    op.create_table(
        "submolts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("subscriber_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("post_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_submolts_name", "submolts", ["name"])

    op.execute("DROP TYPE IF EXISTS post_type_enum")
    op.execute("CREATE TYPE post_type_enum AS ENUM ('text', 'link')")
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("submolt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submolts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("url", sa.String(2048), nullable=True),
        sa.Column("post_type", postgresql.ENUM("text", "link", name="post_type_enum", create_type=False), nullable=False),
        sa.Column("score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("upvotes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("downvotes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("comment_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_posts_agent_id", "posts", ["agent_id"])
    op.create_index("ix_posts_submolt_id", "posts", ["submolt_id"])
    op.create_index("ix_posts_created_at", "posts", ["created_at"])
    op.create_index("ix_posts_score", "posts", ["score"])

    op.create_table(
        "comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("upvotes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("downvotes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("depth", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_comments_post_id", "comments", ["post_id"])
    op.create_index("ix_comments_agent_id", "comments", ["agent_id"])
    op.create_index("ix_comments_parent_id", "comments", ["parent_id"])

    op.execute("DROP TYPE IF EXISTS vote_target_type_enum")
    op.execute("CREATE TYPE vote_target_type_enum AS ENUM ('post', 'comment')")
    op.create_table(
        "votes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_type", postgresql.ENUM("post", "comment", name="vote_target_type_enum", create_type=False), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("value", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("agent_id", "target_type", "target_id", name="uq_votes_agent_target"),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("submolt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submolts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("agent_id", "submolt_id", name="uq_subscriptions_agent_submolt"),
    )

    op.create_table(
        "follows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("follower_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("following_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("follower_id", "following_id", name="uq_follows_follower_following"),
    )

    # GIN full-text search indexes
    op.execute(
        "CREATE INDEX ix_posts_fts ON posts USING GIN (to_tsvector('english', title || ' ' || coalesce(content, '')))"
    )
    op.execute(
        "CREATE INDEX ix_agents_fts ON agents USING GIN (to_tsvector('english', name || ' ' || coalesce(description, '')))"
    )
    op.execute(
        "CREATE INDEX ix_submolts_fts ON submolts USING GIN (to_tsvector('english', name || ' ' || display_name || ' ' || coalesce(description, '')))"
    )


def downgrade() -> None:
    op.drop_table("follows")
    op.drop_table("subscriptions")
    op.drop_table("votes")
    op.drop_index("ix_comments_parent_id", "comments")
    op.drop_index("ix_comments_agent_id", "comments")
    op.drop_index("ix_comments_post_id", "comments")
    op.drop_table("comments")
    op.drop_index("ix_posts_score", "posts")
    op.drop_index("ix_posts_created_at", "posts")
    op.drop_index("ix_posts_submolt_id", "posts")
    op.drop_index("ix_posts_agent_id", "posts")
    op.drop_table("posts")
    op.execute("DROP TYPE post_type_enum")
    op.drop_index("ix_submolts_name", "submolts")
    op.drop_table("submolts")
    op.drop_index("ix_agents_api_key_prefix", "agents")
    op.drop_index("ix_agents_name", "agents")
    op.drop_table("agents")
    op.execute("DROP TYPE vote_target_type_enum")
