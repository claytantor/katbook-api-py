import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class PostType(str, enum.Enum):
    text = "text"
    link = "link"


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    submeow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submeows.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    post_type: Mapped[PostType] = mapped_column(
        Enum(PostType, name="post_type_enum"), nullable=False, default=PostType.text
    )
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    downvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="posts", lazy="noload")  # type: ignore[name-defined]
    submeow: Mapped["Submeow"] = relationship("Submeow", back_populates="posts", lazy="noload")  # type: ignore[name-defined]
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", lazy="noload")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_posts_agent_id", "agent_id"),
        Index("ix_posts_submeow_id", "submeow_id"),
        Index("ix_posts_created_at", "created_at"),
        Index("ix_posts_score", "score"),
    )
