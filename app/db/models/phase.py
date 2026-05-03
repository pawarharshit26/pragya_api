import enum

from sqlalchemy import Date, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import CreateUpdateDeleteModel


class PhaseLifecycle(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETE = "complete"
    ABANDONED = "abandoned"


class Phase(CreateUpdateDeleteModel):
    """
    Time-Boxed Focus
    Examples:
        •	"DSA Foundation - 8 weeks"
        •	"Flute basics - breath control"

    Why
    •	Humans need short horizons
    •	Prevents endless vague goals

    Rules
    •	Phase has start & end dates (schedule)
    •	lifecycle expresses intent (draft/active/paused/complete/abandoned)
    •	Only 1 ACTIVE phase per goal — enforced via partial unique index

    Long-form scope/notes live in Block rows (owner_type="phase").
    """

    __tablename__ = "phase"

    goal_id: Mapped[int] = mapped_column(Integer, ForeignKey("goal.id"), nullable=False)
    goal = relationship("Goal", back_populates="phases")

    title: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date] = mapped_column(Date, nullable=False)
    lifecycle: Mapped[PhaseLifecycle] = mapped_column(
        Enum(PhaseLifecycle, name="phase_lifecycle"),
        nullable=False,
        default=PhaseLifecycle.DRAFT,
        doc="User intent: draft | active | paused | complete | abandoned.",
    )
    outcome: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        doc="Short text — what success looks like for this phase.",
    )

    daily_commitments: Mapped[list] = relationship(
        "DailyCommitment", back_populates="phase"
    )

    __table_args__ = (
        Index(
            "ix_phase_one_active_per_goal",
            "goal_id",
            unique=True,
            postgresql_where=(lifecycle == PhaseLifecycle.ACTIVE),
        ),
    )
