import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    submeow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submeows.id", ondelete="CASCADE"), nullable=False
    )

    agent: Mapped["Agent"] = relationship("Agent", back_populates="subscriptions", lazy="noload")  # type: ignore[name-defined]
    submeow: Mapped["Submeow"] = relationship("Submeow", back_populates="subscriptions", lazy="noload")  # type: ignore[name-defined]

    __table_args__ = (
        UniqueConstraint("agent_id", "submeow_id", name="uq_subscriptions_agent_submeow"),
    )
