"""Runs router."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from orchestron.api.schemas import (
    GetPipelineRunDetailsResponse,
    GetPipelineRunResponse,
    GetPipelineRunsResponse,
)
from orchestron.api.types import DBSessionDependency
from orchestron.db.models import Pipeline, PipelineRun

router = APIRouter(prefix="/pipelines", tags=["Runs"])


@router.get("/{pipeline_id}/runs", response_model=GetPipelineRunsResponse)
async def list_runs(pipeline_id: UUID, db: DBSessionDependency):
    """List all runs of a pipeline."""
    try:
        result = db.query(PipelineRun).filter(PipelineRun.pipeline_id == pipeline_id).all()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not list runs for pipeline with ID {pipeline_id}",
            )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting pipeline runs: {err}",
        ) from err
    else:
        return GetPipelineRunsResponse(
            runs=[GetPipelineRunResponse(id=item.id, status=item.status) for item in result]
        )


@router.get("/{pipeline_id}/runs/{run_id}", response_model=GetPipelineRunDetailsResponse)
async def get_run_details(pipeline_id: UUID, run_id: UUID, db: DBSessionDependency):
    """Get details of a pipeline run."""
    try:
        result = (
            db.query(PipelineRun)
            .filter(PipelineRun.id == run_id, PipelineRun.pipeline.has(Pipeline.id == pipeline_id))
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find run details for pipeline ID {pipeline_id} and run ID {run_id}",  # noqa: E501
            )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting run details: {err}",
        ) from err
    else:
        return result
