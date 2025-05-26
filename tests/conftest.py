"""Fixtures."""

import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from orchestron.api.app import app
from orchestron.db.models import Base, Pipeline, PipelineRun, RunStatus, Step
from orchestron.db.session import SessionManager, get_db_session


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("db")
    db_path = tmp_dir / "test.db"

    return db_path.as_posix()


@pytest.fixture(scope="session", autouse=True)
def session_manager(db_path) -> SessionManager:
    manager = SessionManager(url=f"sqlite:///{db_path}")

    return manager


@pytest.fixture(scope="session")
def dummy_data():
    return {
        "id": uuid.uuid4(),
        "name": "Test pipeline",
        "description": "A test pipeline",
        "created_at": datetime(year=2025, month=5, day=26, hour=13, minute=37, second=0),  # noqa: DTZ001
        "steps": [
            {"name": "Step 1", "command": "echo 'Hello, world!"},
            {"name": "Step 2", "command": "echo 'Hello again'"},
        ],
        "runs": [
            {
                "id": uuid.uuid4(),
                "status": RunStatus.FAILED,
                "start_time": datetime(year=2025, month=5, day=26, hour=13, minute=42, second=0),  # noqa: DTZ001
                "end_time": datetime(year=2025, month=5, day=26, hour=13, minute=42, second=37),  # noqa: DTZ001
            },
            {
                "id": uuid.uuid4(),
                "status": RunStatus.COMPLETED,
                "start_time": datetime(year=2025, month=5, day=26, hour=13, minute=42, second=0),  # noqa: DTZ001
                "end_time": datetime(year=2025, month=5, day=26, hour=14, minute=42, second=0),  # noqa: DTZ001
            },
        ],
    }


@pytest.fixture(scope="session", autouse=True)
def setup_db(session_manager, dummy_data):
    Base.metadata.create_all(bind=session_manager._engine)

    pipeline = Pipeline(
        id=dummy_data["id"],
        name=dummy_data["name"],
        description=dummy_data["description"],
        created_at=dummy_data["created_at"],
        steps=[Step(name=step["name"], command=step["command"]) for step in dummy_data["steps"]],
        runs=[
            PipelineRun(
                id=run["id"],
                status=run["status"],
                start_time=run["start_time"],
                end_time=run["end_time"],
            )
            for run in dummy_data["runs"]
        ],
    )

    session = session_manager.session()
    session.add(pipeline)
    session.flush()
    session.commit()
    session.refresh(pipeline)
    session.close()


@pytest.fixture
def session(session_manager):
    return session_manager.session()


@pytest.fixture
def client(session: Session):
    def get_db_session_override():
        try:
            session.begin()
            yield session
        finally:
            session.rollback()

    app.dependency_overrides[get_db_session] = get_db_session_override

    with TestClient(app) as test_client:
        yield test_client
