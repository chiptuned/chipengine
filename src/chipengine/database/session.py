"""
Database session management for ChipEngine.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import sessionmaker, Session

from . import engine

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Example:
        with get_db_context() as db:
            db.query(Bot).all()
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseSession:
    """
    Class-based session management for use in non-FastAPI contexts.
    """
    
    def __init__(self):
        self.session = None
    
    def __enter__(self) -> Session:
        self.session = SessionLocal()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is not None:
                self.session.rollback()
            self.session.close()
            self.session = None