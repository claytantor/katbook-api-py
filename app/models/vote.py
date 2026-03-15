import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VoteTargetType(str, enum.Enum):
    post = "post"
    comment = "comment"


class Vote(Base, TimestampMixin):
    __tablename__ = "votes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    target_type: Mapped[VoteTargetType] = mapped_column(
        Enum(VoteTargetType, name="vote_target_type_enum"), nullable=False
    )
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)  # +1 or -1

    agent: Mapped["Agent"] = relationship("Agent", back_populates="votes", lazy="noload")  # type: ignore[name-defined]

    __table_args__ = (
        UniqueConstraint("agent_id", "target_type", "target_id", name="uq_votes_agent_target"),
    )
