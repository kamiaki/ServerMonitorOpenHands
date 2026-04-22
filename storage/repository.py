"""Database connection and repository layer."""

import os
from contextlib import contextmanager
from typing import Optional, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base


# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/monitor"
)


class Database:
    """Database connection manager."""

    def __init__(self, url: str = DATABASE_URL):
        """Initialize database connection.

        Args:
            url: Database connection URL.
        """
        self.engine = create_engine(url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables."""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session.

        Yields:
            Database session.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self):
        """Close database connection."""
        self.engine.dispose()


# Default database instance
db = Database()


def get_db() -> Generator[Session, None, None]:
    """Get database session for dependency injection."""
    with db.get_session() as session:
        yield session