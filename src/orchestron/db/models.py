"""DB models."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, UUID, DateTime, ForeignKey, String
from sqlalchemy import Enum as OrmEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class RunStatus(Enum):
    """Pipeline and step runs status."""

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Base(DeclarativeBase):
    """Base class."""

    pass


class Pipeline(Base):
    """ML Pipeline."""

    __tablename__ = "pipelines"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)  # TODO: Use UTC

    steps: Mapped[list["Step"]] = relationship(
        "Step", back_populates="pipeline", cascade="all, delete-orphan"
    )  # TODO: What does cascade do?
    runs: Mapped[list["PipelineRun"]] = relationship(
        "PipelineRun", back_populates="pipeline", cascade="all, delete-orphan"
    )


class Step(Base):
    """ML pipeline step."""

    __tablename__ = "steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    pipeline_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("pipelines.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    command: Mapped[str] = mapped_column(String, nullable=False)
    dependencies: Mapped[list[uuid.UUID]] = mapped_column(
        JSON, default=list, nullable=True
    )  # How do we model dependencies as JSON?

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="steps")
    step_runs: Mapped[list["StepRun"]] = relationship("StepRun", back_populates="step")


class PipelineRun(Base):
    """ML pipeline run."""

    __tablename__ = "pipeline_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    pipeline_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("pipelines.id"), nullable=False)
    status: Mapped[RunStatus] = mapped_column(
        OrmEnum(RunStatus), default=RunStatus.PENDING, nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    run_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=True)

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="runs")
    step_runs: Mapped[list["StepRun"]] = relationship("StepRun", back_populates="pipeline_run")


class StepRun(Base):
    """ML pipeline step run."""

    __tablename__ = "step_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    pipeline_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("steps.id"), nullable=False)
    pipeline_run_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("pipeline_runs.id"), nullable=False
    )
    status: Mapped[RunStatus] = mapped_column(
        OrmEnum(RunStatus), default=RunStatus.PENDING, nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    step: Mapped["Step"] = relationship("Step", back_populates="step_runs")
    pipeline_run: Mapped["PipelineRun"] = relationship("PipelineRun", back_populates="step_runs")
