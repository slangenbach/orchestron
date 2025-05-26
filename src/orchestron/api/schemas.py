"""API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from orchestron.db.models import RunStatus


class RegisterPipelineRequest(BaseModel):
    """Register pipeline request."""

    name: str
    description: str | None = None


class RegisterPipelineResponse(BaseModel):
    """Register pipeline response."""

    id: UUID


class GetPipelineResponse(BaseModel):
    """Get pipeline response."""

    id: UUID
    name: str


class GetPipelineDetailsResponse(GetPipelineResponse):
    """Get pipeline details response."""

    description: str | None
    created_at: datetime


class ListPipelinesResponse(BaseModel):
    """List pipeline response."""

    pipelines: list[GetPipelineResponse | None]


class GetPipelineRunResponse(BaseModel):
    """Get pipeline run response."""

    id: UUID
    status: RunStatus


class GetPipelineRunDetailsResponse(GetPipelineRunResponse):
    """Get pipeline run details response."""

    start_time: datetime
    end_time: datetime | None


class GetPipelineRunsResponse(BaseModel):
    """Get pipeline runs response."""

    runs: list[GetPipelineRunResponse | None]
