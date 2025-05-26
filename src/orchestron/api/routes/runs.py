"""Runs router."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from orchestron.api.schemas import (
    GetPipelineRunDetailsResponse,
    GetPipelineRunResponse,
    GetPipelineRunsResponse,
)
from orchestron.api.types import DBSessionDependency
from orchestron.db.models import PipelineRun

router = APIRouter(prefix="/pipelines", tags=["Runs"])


@router.get("/{pipeline_id}/runs", response_model=GetPipelineRunsResponse)
async def list_runs(pipeline_id: UUID, db: DBSessionDependency):
    """List all runs of a pipeline."""
    try:
        result = db.query(PipelineRun).filter(PipelineRun.pipeline_id == pipeline_id).all()
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not list runs for pipeline with ID {pipeline_id}",
        ) from err
    else:
        return GetPipelineRunsResponse(
            runs=[GetPipelineRunResponse(id=item.id, status=item.status) for item in result]
        )


@router.get("/{pipeline_id}/runs/{run_id}", response_model=GetPipelineRunDetailsResponse)
async def get_run_details(pipeline_id: UUID, run_id: UUID, db: DBSessionDependency):
    """Get details of a pipeline run."""
    try:
        result = db.query(PipelineRun).filter(
            PipelineRun.pipeline == pipeline_id, PipelineRun.pipeline.has(PipelineRun.id == run_id)
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find pipeline with ID {pipeline_id}: {err}",
        ) from err
    else:
        return result
