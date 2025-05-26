"""Pipelines router."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from orchestron.api.schemas import (
    GetPipelineDetailsResponse,
    GetPipelineResponse,
    ListPipelinesResponse,
    RegisterPipelineRequest,
    RegisterPipelineResponse,
)
from orchestron.api.types import DBSessionDependency
from orchestron.db.models import Pipeline, Step

router = APIRouter(prefix="/pipelines", tags=["Pipeline"])


@router.post("/", response_model=RegisterPipelineResponse, status_code=status.HTTP_201_CREATED)
async def register_pipeline(request: RegisterPipelineRequest, db: DBSessionDependency):
    """Register a new pipeline."""
    pipeline = Pipeline(name=request.name, description=request.description)

    try:
        db.add(pipeline)
        db.flush()

        for data in pipeline.steps:
            step = Step(
                name=data.name,
                command=data.command,
                dependencies=data.dependencies,
                pipeline_id=pipeline.id,
            )
            db.add(step)

        db.commit()
        db.refresh(pipeline)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not register pipeline: {err}",
        ) from err
    else:
        return RegisterPipelineResponse(id=pipeline.id)


@router.get("/", response_model=ListPipelinesResponse)
async def list_pipelines(db: DBSessionDependency):
    """List all pipelines."""
    try:
        result = db.query(Pipeline).all()  # TODO: Add limit
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not list pipelines."
        ) from err
    else:
        return ListPipelinesResponse(
            pipelines=[
                GetPipelineResponse(
                    # TODO: Transform UUID to str within model.
                    id=str(item.id),  # ty: ignore[invalid-argument-type]
                    name=item.name,
                )
                for item in result
            ]
        )


@router.get("/{pipeline_id}", response_model=GetPipelineDetailsResponse)
async def get_pipeline_details(pipeline_id: UUID, db: DBSessionDependency):
    """Get details of a specific pipeline."""
    try:
        result = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not get details for pipeline with ID {pipeline_id}",
        ) from err
    else:
        return result
