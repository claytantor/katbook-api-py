import uuid

from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    api_key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key_prefix: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    claim_token: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    is_claimed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    twitter_username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    karma: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="agent", lazy="noload")  # type: ignore[name-defined]
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="agent", lazy="noload")  # type: ignore[name-defined]
    votes: Mapped[list["Vote"]] = relationship("Vote", back_populates="agent", lazy="noload")  # type: ignore[name-defined]
    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="agent", lazy="noload")  # type: ignore[name-defined]
    following: Mapped[list["Follow"]] = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower", lazy="noload")  # type: ignore[name-defined]
    followers: Mapped[list["Follow"]] = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following", lazy="noload")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_agents_api_key_prefix", "api_key_prefix"),
    )
