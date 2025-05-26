"""DB session."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from orchestron.config import get_config
from orchestron.db.models import Base


class SessionManager:
    """DB Session Manager."""

    def __init__(self, url: str) -> None:  # noqa: D107
        self._engine = create_engine(
            url=url,
            connect_args={"check_same_thread": False},
        )
        self._sessionmaker = sessionmaker(autocommit=False, bind=self._engine)

    def connect(self):
        """Connect to DB."""
        with self._engine.begin() as connection:
            try:
                return connection
            except Exception:
                connection.rollback()
                raise

    def close(self):
        """Close DB connection."""
        self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    def session(self):
        """Get DB session."""
        session = self._sessionmaker()

        try:
            return session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def init_db(engine: Engine) -> None:
    """Initialize database."""
    Base.metadata.create_all(bind=engine)


def get_db_session(url: str | None) -> Session:
    """Get DB session."""
    if not url:
        config = get_config()
        url = config.db_url

    session_manager = SessionManager(url)
    return session_manager.session()
