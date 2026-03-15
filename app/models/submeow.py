import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Submeow(Base, TimestampMixin):
    __tablename__ = "submeows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True
    )
    subscriber_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    post_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    creator: Mapped["Agent"] = relationship("Agent", lazy="noload")  # type: ignore[name-defined]
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="submeow", lazy="noload")  # type: ignore[name-defined]
    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="submeow", lazy="noload")  # type: ignore[name-defined]
