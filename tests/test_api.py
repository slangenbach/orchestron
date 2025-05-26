from fastapi import status
from fastapi.testclient import TestClient

from orchestron.api.schemas import (
    GetPipelineDetailsResponse,
    GetPipelineResponse,
    GetPipelineRunDetailsResponse,
    GetPipelineRunResponse,
    GetPipelineRunsResponse,
    ListPipelinesResponse,
    RegisterPipelineRequest,
)
from orchestron.db.models import RunStatus


def test_list_pipelines(client: TestClient, dummy_data):
    expected = ListPipelinesResponse(
        pipelines=[
            GetPipelineResponse(
                id=str(dummy_data["id"]),  # ty: ignore[invalid-argument-type]
                name=dummy_data["name"],
            )
        ]
    )
    actual = client.get("/pipelines")

    assert actual.json() == expected.model_dump(mode="json")


def test_get_pipeline_details(client: TestClient, dummy_data):
    expected = GetPipelineDetailsResponse(
        id=dummy_data["id"],
        name=dummy_data["name"],
        description=dummy_data["description"],
        created_at=dummy_data["created_at"],
    )

    actual = client.get(f"/pipelines/{str(dummy_data['id'])}")

    assert actual.json() == expected.model_dump(mode="json")


def test_register_pipeline(client: TestClient, dummy_data):
    data = RegisterPipelineRequest(
        name="Another test pipeline", description="Fresh out of the oven"
    )
    response = client.post("/pipelines/", json=data.model_dump())
    new_pipeline_id = response.json().get("id")

    assert response.status_code == status.HTTP_201_CREATED

    actual = client.get(f"/pipelines/{new_pipeline_id}")
    actual_data = actual.json()

    assert actual_data["id"] == new_pipeline_id
    assert actual_data["name"] == data.name
    assert actual_data["description"] == data.description


def test_list_runs(client: TestClient, dummy_data):
    expected = GetPipelineRunsResponse(
        runs=[
            GetPipelineRunResponse(
                id=run["id"],
                status=run["status"],
            )
            for run in dummy_data["runs"]
        ]
    )

    actual = client.get(f"/pipelines/{str(dummy_data['id'])}/runs")

    assert actual.json() == expected.model_dump(mode="json")


def test_get_run_details(client: TestClient, dummy_data):
    run = dummy_data["runs"][0]
    expected = GetPipelineRunDetailsResponse(
        id=run["id"],
        status=run["status"],
        start_time=run["start_time"],
        end_time=run["end_time"],
    )

    actual = client.get(
        f"/pipelines/{str(dummy_data['id'])}/runs/{str(dummy_data['runs'][0]['id'])}"
    )

    assert actual.json() == expected.model_dump(mode="json")


def test_trigger_run(client: TestClient, dummy_data):
    pipeline_id = str(dummy_data["id"])
    response = client.post(f"/pipelines/{pipeline_id}/trigger_run")

    assert response.status_code == status.HTTP_201_CREATED

    new_run_id = response.json().get("id")

    actual = client.get(f"/pipelines/{pipeline_id}/runs/{new_run_id}")
    data = actual.json()

    assert data["id"] == new_run_id
    assert data["status"] == RunStatus.PENDING.value
