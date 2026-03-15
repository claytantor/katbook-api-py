"""rename_submolts_to_submeows

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-14

Renames:
  - table:  submolts          → submeows
  - column: posts.submolt_id  → posts.submeow_id
  - column: subscriptions.submolt_id → subscriptions.submeow_id
  - index:  ix_submolts_name         → ix_submeows_name
  - index:  ix_posts_submolt_id      → ix_posts_submeow_id
  - constraint: uq_subscriptions_agent_submolt → uq_subscriptions_agent_submeow
  - FTS index: ix_submolts_fts       → ix_submeows_fts
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename table
    op.rename_table("submolts", "submeows")

    # 2. Rename foreign key columns
    op.alter_column("posts", "submolt_id", new_column_name="submeow_id")
    op.alter_column("subscriptions", "submolt_id", new_column_name="submeow_id")

    # 3. Rename indexes on submeows table
    op.execute("ALTER INDEX ix_submolts_name RENAME TO ix_submeows_name")

    # 4. Rename index on posts
    op.execute("ALTER INDEX ix_posts_submolt_id RENAME TO ix_posts_submeow_id")

    # 5. Rename unique constraint on subscriptions
    op.execute(
        "ALTER TABLE subscriptions "
        "RENAME CONSTRAINT uq_subscriptions_agent_submolt TO uq_subscriptions_agent_submeow"
    )

    # 6. Drop old FTS index and recreate pointing at new table name
    op.execute("DROP INDEX IF EXISTS ix_submolts_fts")
    op.execute(
        "CREATE INDEX ix_submeows_fts ON submeows "
        "USING GIN (to_tsvector('english', name || ' ' || display_name || ' ' || coalesce(description, '')))"
    )

    # 7. Update FK constraint names (PostgreSQL auto-named on create)
    #    posts: fk posts_submolt_id_fkey → posts_submeow_id_fkey
    op.execute(
        "ALTER TABLE posts "
        "RENAME CONSTRAINT posts_submolt_id_fkey TO posts_submeow_id_fkey"
    )
    #    subscriptions: fk subscriptions_submolt_id_fkey → subscriptions_submeow_id_fkey
    op.execute(
        "ALTER TABLE subscriptions "
        "RENAME CONSTRAINT subscriptions_submolt_id_fkey TO subscriptions_submeow_id_fkey"
    )


def downgrade() -> None:
    # Reverse FK constraint renames
    op.execute(
        "ALTER TABLE subscriptions "
        "RENAME CONSTRAINT subscriptions_submeow_id_fkey TO subscriptions_submolt_id_fkey"
    )
    op.execute(
        "ALTER TABLE posts "
        "RENAME CONSTRAINT posts_submeow_id_fkey TO posts_submolt_id_fkey"
    )

    # Reverse FTS index
    op.execute("DROP INDEX IF EXISTS ix_submeows_fts")
    op.execute(
        "CREATE INDEX ix_submolts_fts ON submolts "
        "USING GIN (to_tsvector('english', name || ' ' || display_name || ' ' || coalesce(description, '')))"
    )

    # Reverse unique constraint
    op.execute(
        "ALTER TABLE subscriptions "
        "RENAME CONSTRAINT uq_subscriptions_agent_submeow TO uq_subscriptions_agent_submolt"
    )

    # Reverse post index
    op.execute("ALTER INDEX ix_posts_submeow_id RENAME TO ix_posts_submolt_id")

    # Reverse submeows table index
    op.execute("ALTER INDEX ix_submeows_name RENAME TO ix_submolts_name")

    # Reverse column renames
    op.alter_column("subscriptions", "submeow_id", new_column_name="submolt_id")
    op.alter_column("posts", "submeow_id", new_column_name="submolt_id")

    # Reverse table rename
    op.rename_table("submeows", "submolts")
