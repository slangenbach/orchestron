"""API types."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from orchestron.db.session import get_db_session

DBSessionDependency = Annotated[Session, Depends(get_db_session)]
